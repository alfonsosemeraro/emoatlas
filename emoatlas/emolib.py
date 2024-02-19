"""
@author: alfonso.semeraro@unito.it

"""

from emoatlas.resources import (
    _load_spacy,
    _load_dictionary,
    _load_emojis,
    _load_antonyms,
    _load_idiomatic_tokens,
    _load_stemmer,
)
import emoatlas.formamentis_edgelist as fme
import emoatlas.emo_scores as es
import emoatlas.baselines as bsl
import emoatlas.draw_plutchik as dp
from emoatlas.baselines import _load_lookup_table, _make_baseline
import emoatlas.draw_formamentis_force as dff
import emoatlas.draw_formamentis_bundling as dfb


class EmoScores:
    def __init__(self, language="english", spacy_model=None, emotion_model="plutchik"):

        # Basic imports
        self.language = language
        self._emotion_lexicon = _load_dictionary(language)
        if spacy_model is None:
            self._tagger = _load_spacy(language)
        else:
            self._tagger =  _load_spacy(model = spacy_model)
        self._stemmer = None
        self._stem_or_lem = "lemmatization"
        self._emotionlist = None
        self._emojis_dict = _load_emojis(language)
        self._idiomatic_tokens = _load_idiomatic_tokens(language)

        # Formamentis imports
        self._antonyms = _load_antonyms(language)

        # Z-scores imports
        self._baseline = _make_baseline(
            language=self.language, emotion_lexicon=self._emotion_lexicon
        )
        self._lookup = _load_lookup_table(language=self.language)

        if emotion_model == "plutchik":
            self.emotionslist = [
                "anger",
                "trust",
                "surprise",
                "disgust",
                "joy",
                "sadness",
                "fear",
                "anticipation",
            ]
            self._emotion_model = "plutchik"

    def set_stemming_lemmatization(self, stem_or_lem="lemmatization"):

        self._emotion_lexicon = _load_dictionary(self.language, stem_or_lem)
        self._idiomatic_tokens = _load_idiomatic_tokens(self.language, stem_or_lem)
        self._stem_or_lem = stem_or_lem

        if stem_or_lem == "stemming" and self._stemmer is None:
            self._stemmer = _load_stemmer(self.language)

    def set_baseline(self, baseline=None):
        """
        Set a new emotion distribution as baseline to compute zscores.
        If no baseline is provided, a new one will be created from the default emotion lexicon loaded.

        Required arguments:
        ----------

        *baseline*:
            Either a list of lists, a text, or None.
            If baseline is a list of list, it contains the distribution of emotions of the text used as baseline.
            If baseline is a text, a new emotion distribution will be computed from it.
            If baseline is None, it will be computed the emotion distribution of the default emotion lexicon loaded.

        """
        self._baseline = bsl._make_baseline(
            baseline,
            emotion_lexicon=self._emotion_lexicon,
            tagger=self._tagger,
            emojis_dict=self._emojis_dict,
            idiomatic_tokens=self._idiomatic_tokens,
        )
        self._lookup = {}

    def emotions(
        self,
        obj,
        normalization_strategy="none",
        return_words=False,
        convert_emojis=True,
    ):

        """
        Count emotions in an input text or Formamentis Network.

        Required arguments:
        ----------

        *obj*:
            Either a string or a list of tuples, with the former being the text to extract emotion from,
            and the latter being the standard representation of a formamentis edgelist.

        *normalization_strategy*:
            A string, whether to normalize emotion scores over the number of words. Accepted values are:
                'none': no normalization at all
                'text_lenght': normalize emotion counts over the total text length
                'emotion_words': normalize emotion counts over the number of words associated to an emotion

        *return_words*:
            A bool. Whether to return a list of the words associated with each of the emotions, or just their count.

        *convert_emojis*:
            A bool. Whether to convert emojis in raw text to be processed, or not.


        Returns:
        ----------
        *emotions*:
            A dict. Keys are emotions, and values the scores.
        """

        model = self._tagger if self._stem_or_lem == "lemmatization" else self._stemmer

        return es._get_emotions(
            obj=obj,
            normalization_strategy=normalization_strategy,
            emotion_lexicon=self._emotion_lexicon,
            language=self.language,
            tagger=model,
            emotions=self.emotionslist,
            return_words=return_words,
            emojis_dict=self._emojis_dict,
            convert_emojis=convert_emojis,
            idiomatic_tokens=self._idiomatic_tokens,
        )

    def zscores(self, obj, baseline=None, n_samples=300, convert_emojis=True):

        """
        Checks the emotion distribution in an input text or Formamentis Network against a baseline, and returns the z-scores.

        Required arguments:
        ----------

        *obj*:
            Either a string or a list of tuples, with the former being the text to extract emotion from,
            and the latter being the standard representation of a formamentis edgelist.

        *baseline*:
            Either a list of lists, a text, or None.
            If baseline is a list of list, it contains the distribution of emotions of the text used as baseline.
            If baseline is a text, a new emotion distribution will be computed from it.
            If baseline is None, it will be computed the emotion distribution of the default emotion lexicon loaded.

        *n_samples*:
            An integer, how many time the baseline emotion distribution will be sampled before checking for z-scores.
            Default is 300.

        *convert_emojis*:
            A bool. Whether to convert emojis in raw text to be processed, or not.

        Returns:
        ----------
        *z-scores*:
            A dict. Keys are emotions, and values the z-scores.

        """

        model = self._tagger if self._stem_or_lem == "lemmatization" else self._stemmer

        if not baseline:
            if not self._baseline:
                self._baseline = bsl._make_baseline(
                    baseline=None,
                    tagger=model,
                    language=self.language,
                    emotion_lexicon=self._emotion_lexicon,
                )
            baseline = self._baseline
        else:
            baseline = bsl._make_baseline(
                baseline=baseline,
                tagger=model,
                language=self.language,
                emotion_lexicon=self._emotion_lexicon,
            )

        return es._zscores(
            obj,
            baseline=baseline,
            n_samples=n_samples,
            emotion_lexicon=self._emotion_lexicon,
            language=self.language,
            tagger=model,
            emotions=self.emotionslist,
            lookup=self._lookup,
            emojis_dict=self._emojis_dict,
            convert_emojis=convert_emojis,
            idiomatic_tokens=self._idiomatic_tokens,
        )

    def formamentis_network(
        self,
        text,
        target_word=None,
        keepwords=[],
        stopwords=[],
        max_distance=3,
        semantic_enrichment="synonyms",
        multiplex=False,
        with_type=False,
    ):
        """
        Extract a Formamentis Network from input text.

        Required arguments:
        ----------

        *text*:
            A string, the text to extract emotions from.

        *target_word*:
            A string or None. If a string and method is 'formamentis', it will be computed the emotion distribution
            only of the neighborhood of 'target_word' in the formamentis network.

        *keepwords*:
            A list. Words that shall be included in formamentis networks regardless from their part of speech. Default is an empty list.
            By default implementation, a pre-compiled list of negations and pronouns will be loaded and used as keepwords.

        *stopwords*:
            A list. Words that shall be discarded from formamentis networks regardless from their part of speech. Default is an empty list.
            If a word is both in stopwords and in keepwords, the word will be discarded.

        *max_distance*:
            An integer, by default 2. Links in the formamentis network will be established from each word to each neighbor within a distance
            defined by max_distance.

        *semantic_enrichment*:
            A str or a list of str. If 'synonyms', will be added semantic arcs between synonyms into the network. If 'hypernyms', will be
            added semantic arcs between hypernyms and hyponyms. Also ['synonyms', 'hypernyms'] is accepted.

        *multiplex*:
            A bool: whether to return different edgelist for different kinds of edges (syntactic, synonyms, hypernyms) or not. Default is False.


        Returns:
        ----------
        *fmn*:
            A Formamentis Network in the form of (Edges, Vertices).

        """

        return fme.get_formamentis_edgelist(
            text,
            language=self.language,
            spacy_model=self._tagger,
            stemmer=self._stemmer,
            stem_or_lem=self._stem_or_lem,
            target_word=target_word,
            keepwords=keepwords,
            stopwords=stopwords,
            antonyms=self._antonyms,
            max_distance=max_distance,
            semantic_enrichment=semantic_enrichment,
            multiplex=multiplex,
            idiomatic_tokens=self._idiomatic_tokens,
        )

    def draw_formamentis(
        self, fmn, layout="edge_bundling", highlight=[], thickness=1, ax=None, translated=False,
    ):
        """
        Represents a Formamentis Network in either a circular or force-based layout.

        Required arguments:
        ----------

        *fmn*:
            A Formamentis Network to visualize.

        *layout*:
            A str. Either "edge_bundling" for circular layout or "force_layout" for force-based layout.

        *highlight*:
            A list of the words to highlight in the network.

        *thickness*:
            A numeric. How thick must lines be drawn. Default is 1.

        *ax*:
            A matplotlib axes to draw the network on. If none is provided, a new one will be created.

        *translated*:
            A boolean value. True for english-translated nodes, False for original node labels. Default is False.
        """

        if layout == "force_layout":
            dff.draw_formamentis_force_layout(
                fmn.edges,
                highlight=highlight,
                language=self.language,
                thickness=thickness,
                ax=ax,
                translated=translated
            )
        elif layout == "edge_bundling":
            dfb.draw_formamentis_circle_layout(
                fmn,
                highlight=highlight,
                language=self.language,
                thickness=thickness,
                ax=ax,
                translated=translated
            )

    def draw_statistically_significant_emotions(self, obj):
        """
        Computes how statistically significantly higher or lower is each emotion in the input text or Formamentis Network.
        It draws the Plutchik's flower highlighting only emotions over/under represented w.r.t. a neutral baseline.
        This function is a wrapper of
            zs = zscores(obj)
            draw_plucthik(zs, reject_range = [-1.96, 1.96])

        Required arguments:
        ----------

        *obj*:
            A str or a Formamentis Network to search emotions in.

        *reject_range*:
            A threshold for significance of zscores. A zscore higher (lower) than 1.96 (-1.96) means that an emotion is
            statistically over (under) represented (p-value = 0.05).
        """
        zs = self.zscores(obj)
        self.draw_plutchik(zs, reject_range=[-1.96, 1.96])

    def draw_formamentis_flower(
        self,
        text,
        target_word=None,
        keepwords=[],
        stopwords=[],
        max_distance=3,
        semantic_enrichment=[],
        reject_range=(-1.96, 1.96),
    ):

        """
        Draw a Plutchik's wheel of emotions based on a Formamentis Network built upon input text.
        This function is a wrapper of
            fmn = formamentis_network(text, target_word = target_word)
            zs = zscores(fmn)
            draw_plutchik(zs, reject_range = (-1.96, 1.96))

        Required arguments:
        ----------

        *text*:
            A string, the text to extract the Formamentis_Network from.

        *target_word*:
            A string or None. If a string and method is 'formamentis', it will be computed the emotion distribution
            only of the neighborhood of 'target_word' in the formamentis network.

        *keepwords*:
            A list. Words that shall be included in formamentis networks regardless from their part of speech. Default is an empty list.
            By default implementation, a pre-compiled list of negations and pronouns will be loaded and used as keepwords.

        *stopwords*:
            A list. Words that shall be discarded from formamentis networks regardless from their part of speech. Default is an empty list.
            If a word is both in stopwords and in keepwords, the word will be discarded.

        *max_distance*:
            An integer, by default 2. Links in the formamentis network will be established from each word to each neighbor within a distance
            defined by max_distance.

        *semantic_enrichment*:
            A str or a list of str. If 'synonyms', will be added semantic arcs between synonyms into the network. If 'hyperonyms', will be
            added semantic arcs between hyperonyms and hyponyms. Also ['synonyms', 'hyperonyms'] is accepted.


        *reject_range*:
            A threshold for significance of zscores. A zscore higher (lower) than 1.96 (-1.96) means that an emotion is
            statistically over (under) represented (p-value = 0.05).

        """
        fmn = self.formamentis_network(
            text,
            target_word=target_word,
            keepwords=keepwords,
            stopwords=stopwords,
            semantic_enrichment=semantic_enrichment,
            max_distance=max_distance,
        )

        zs = self.zscores(fmn)
        self.draw_plutchik(zs, reject_range=(-1.96, 1.96))

    def draw_plutchik(
        self,
        scores,
        ax=None,
        rescale=False,
        reject_range=None,
        highlight="all",
        show_intensity_levels="none",
        font=None,
        fontweight="light",
        fontsize=15,
        show_coordinates=True,
        show_ticklabels=False,
        ticklabels_angle=0,
        ticklabels_size=11,
        height_width_ratio=1,
        title=None,
        title_size=None,
    ):

        """
        Draw the emotions or dyads Plutchik flower.
        Full details at https://github.com/alfonsosemeraro/pyplutchik/blob/master/Documentation.md

        Required arguments:
        ----------

        *scores*:
            A dictionary with emotions or dyads.
            For each entry, values accepted are a 3-values iterable (for emotions only) or a scalar value between 0 and 1.
            The sum of the 3-values iterable values must not exceed 1, and no value should be negative.
            See emo_params() and dyad_params() for accepted keys.

            Emotions and dyads are mutually exclusive. Different kinds of dyads are mutually exclusive.

        *ax*:
            Axes to draw the coordinates.

        *rescale*:
            Either None or a 2-item tuple, with minimum and maximum value of the printable area.

        *reject_range*:
            A 2-item tuple. All petal scores that fall within the range must be considered non-interesting, thus drawed in grey.
            Default is None (no range at all).

        *highlight*:
            A string or a list of main emotions to highlight. If a list of emotions is given, other emotions will be shadowed.
            Default is 'all'.

        *show_intensity_levels*:
            A string or a list of main emotions. It shows all three intensity scores for each emotion in the list,
            and for the others cumulative scores. Default is 'none'.

        *font*:
            Font of text. Default is sans-serif.

        *fontweight*:
            Font weight of text. Default is light.

        *fontsize*:
            Font size of text. Default is 15.

        *show_coordinates*:
            A boolean, wether to show polar coordinates or not.

        *show_ticklabels*:
            Boolean, wether to show tick labels under Joy petal. Default is False.

        *ticklabels_angle*:
            How much to rotate tick labels from y=0. Value should be given in radians. Default is 0.

        *ticklabels_size*:
            Size of tick labels. Default is 11.

        *height_width_ratio*:
            Ratio between height and width of the petal. Lower the ratio, thicker the petal. Default is 1.

        *title*:
            Title for the plot.

        *title_size*:
            Size of the title. Default is font_size.

        Returns:
        ----------
        *ax*:
            The input Axes modified, if provided, otherwise a new generated one.

        """

        dp.draw_plutchik(
            scores,
            ax=ax,
            rescale=rescale,
            reject_range=reject_range,
            highlight=highlight,
            show_intensity_levels=show_intensity_levels,
            font=font,
            fontweight=fontweight,
            fontsize=fontsize,
            show_coordinates=show_coordinates,
            show_ticklabels=show_ticklabels,
            ticklabels_angle=ticklabels_angle,
            ticklabels_size=ticklabels_size,
            height_width_ratio=height_width_ratio,
            title=title,
            title_size=title_size,
        )
