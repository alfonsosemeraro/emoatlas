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

from emoatlas.textloader import _load_object
from collections import defaultdict, namedtuple
import emoatlas.formamentis_edgelist as fme
import emoatlas.emo_scores as es
import emoatlas.baselines as bsl
import emoatlas.draw_plutchik as dp
from emoatlas.baselines import _load_lookup_table, _make_baseline
import emoatlas.draw_formamentis_force as dff
import emoatlas.draw_formamentis_bundling as dfb
import matplotlib.pyplot as plt
from matplotlib import patches
from emoatlas.resources import _valences
import networkx as nx
import itertools
import os


class EmoScores:
    def __init__(self, language="english", spacy_model=None, emotion_model="plutchik"):

        # Basic imports
        self.language = language
        self._emotion_lexicon = _load_dictionary(language)
        if spacy_model is None:
            self._tagger = _load_spacy(language)
        else:
            self._tagger = _load_spacy(model=spacy_model)
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
        self,
        fmn,
        layout="edge_bundling",
        highlight=[],
        thickness=1,
        ax=None,
        hide_label=False,
        translated=False,
        alpha_syntactic=0.5,
        alpha_hypernyms=0.5,
        alpha_synonyms=0.5,
        save_path=None,
        custom_valences=None,
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

        *hide_label*:
            A boolean value. If True, labels of words will not be visible.

        *translated*:
            A boolean value. True for english-translated nodes, False for original node labels. Default is False.

        *alpha_syntactic*:
            A numeric. Alpha value for syntactic edges, must be between 0.0 and 1.0

        *alpha_hypernyms*:
            A numeric. Alpha value for hypernyms edges, must be between 0.0 and 1.0

        *alpha_synonyms*:
            A numeric. Alpha value for synonyms edges, must be between 0.0 and 1.0

        *save_path*:
            A string representing the file path where the figure should be saved.
            If None, the figure will only be plotted and not saved. Default is None.

        *custom_valences*:
            A list of 3 sets: positive, negative and neutral custom valences. Default is None.
            Currently only employed for edge_bundling.
        """
        
        if custom_valences is not None:
            if type(custom_valences) != list and len(custom_valences) != 3:
                raise ValueError("Custom valences must be a list of 3 sets: positive, negative and neutral")
            elif type(custom_valence[0] != set):
                raise ValueError("Custom valences must be a list of 3 sets: positive, negative and neutral")
            elif type(custom_valence[1] != set):
                raise ValueError("Custom valences must be a list of 3 sets: positive, negative and neutral")
            elif type(custom_valence[2] != set):
                raise ValueError("Custom valences must be a list of 3 sets: positive, negative and neutral")


        # Check if alpha values are within the range [0.0, 1.0]
        if not (0.0 <= alpha_syntactic <= 1.0):
            raise ValueError("Alpha value for syntactic must be between 0.0 and 1.0")
        if not (0.0 <= alpha_hypernyms <= 1.0):
            raise ValueError("Alpha value for hypernyms must be between 0.0 and 1.0")
        if not (0.0 <= alpha_synonyms <= 1.0):
            raise ValueError("Alpha value for synonyms must be between 0.0 and 1.0")

        if layout == "force_layout":
            dff.draw_formamentis_force_layout(
                fmn.edges,
                highlight=highlight,
                language=self.language,
                thickness=thickness,
                ax=ax,
                hide_label=hide_label,
                translated=translated,
                alpha_syntactic=alpha_syntactic,
                alpha_hypernyms=alpha_hypernyms,
                alpha_synonyms=alpha_synonyms,
                save_path=save_path
                )
        elif layout == "edge_bundling":
            dfb.draw_formamentis_circle_layout(
                fmn,
                highlight=highlight,
                language=self.language,
                thickness=thickness,
                ax=ax,
                hide_label=hide_label,
                translated=translated,
                alpha_syntactic=alpha_syntactic,
                alpha_hypernyms=alpha_hypernyms,
                alpha_synonyms=alpha_synonyms,
                save_path=save_path,
                custom_valences=custom_valences,
            )

    def extract_word_from_formamentis(self, fmn, target_word):
        """
        Extract the semantic frame of a single word from a formamentis network.

        Required arguments:
        *fmn*:
            The formamentis from which the word must be extracted.
        *target_word*:
            A string. Only the edges that are related to this word will be extracted.

        ----------
        Returns:
        *fmnt*:
            A Formamentis Network of the target word.
        """

        if type(fmn.edges) != dict:
            # Get our vertices set
            new_edgelist = [edge for edge in fmn.edges if target_word in edge]
            final_vertex = set(itertools.chain(*new_edgelist))

            # If both words of each edgelist are in our vertices, consider them.
            final_edgelist = [
                edge
                for edge in fmn.edges
                if (edge[0] in final_vertex) and (edge[1] in final_vertex)
            ]

            FormamentisNetwork = namedtuple("FormamentisNetwork", "edges vertices")
            return FormamentisNetwork(final_edgelist, list(final_vertex))
        else:

            # Get our vertices set
            final_vertex = set()
            edge_types = list(fmn.edges.keys())
            for edge_type in edge_types:
                new_edgelist = [
                    edge for edge in fmn.edges[edge_type] if target_word in edge
                ]
                final_vertex = final_vertex | set(itertools.chain(*new_edgelist))

            # If both words of each edgelist are in our vertices, consider them.
            final_edgelist = {}
            for edge_type in edge_types:
                new_edgelist = [
                    edge
                    for edge in fmn.edges[edge_type]
                    if (edge[0] in final_vertex) and (edge[1] in final_vertex)
                ]
                final_edgelist[edge_type] = new_edgelist

            FormamentisNetwork = namedtuple("FormamentisNetwork", "edges vertices")
            return FormamentisNetwork(final_edgelist, list(final_vertex))

    def draw_statistically_significant_emotions(self, obj, title=None):
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

        *title*:
            Title for the plot.

        """
        zs = self.zscores(obj)
        self.draw_plutchik(zs, title=title, reject_range=[-1.96, 1.96])

    def draw_formamentis_flower(
        self,
        text,
        target_word=None,
        keepwords=[],
        stopwords=[],
        max_distance=3,
        semantic_enrichment=[],
        reject_range=(-1.96, 1.96),
        title=None,
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

        *title*:
            Title for the plot.

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
        self.draw_plutchik(zs, title=title, reject_range=(-1.96, 1.96))

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

    # Used if you are only interested in lemmatizing texts
    def lemmatize_text(
        self,
        text,
    ):

        lemmatized = _load_object(
            text,
            language=self.language,
            tagger=self._tagger,
            idiomatic_tokens={},
            convert_emojis=True,
            emojis_dict=self._emojis_dict,
        )

        fmnt = fme.get_formamentis_edgelist(
            text,
            language=self.language,
            spacy_model=self._tagger,
            stemmer=self._stemmer,
            stem_or_lem=self._stem_or_lem,
            antonyms=self._antonyms,
            idiomatic_tokens={},
        )

        lemmatized = [word for word in lemmatized if word in fmnt.vertices]

        return lemmatized

    ######################################
    # Utilities
    ######################################

    def export_formamentis(self, fmnt, filename=None, path=None):
        """
        Export the edges of a Formamentis Network to a text file. Does not support multiplex.

        Parameters:
        -----------
        fmnt : FormamentisNetwork
            The Formamentis Network object to extract edges from.
        path : str, optional
            The directory path to save the file. Defaults to the current working directory.
        filename : str, optional
            The name of the file to save. Defaults to 'extracted_formamentis.txt'.

        Returns:
        --------
        None
        """

        if filename == None:
            filename = "extracted formamentis.txt"
        elif not filename.endswith(".txt"):
            filename += ".txt"

        if path == None:
            path = os.getcwd()

        # Combine path and filename to get the full file path
        filepath = os.path.join(path, filename)

        edges = fmnt.edges

        with open(filepath, "w") as file:
            for pair in edges:
                file.write(f"{pair[0]} , {pair[1]}\n")

    def import_formamentis(self, filepath=None):
        """
        Import the edges of a Formamentis Network from a text file. Does not support multiplex.

        Parameters:
        -----------
        filepath : str, optional
            The path of the file from which to import files.

        Returns:
        --------
        fmnt : FormamentisNetwork
            The Formamentis Network object.
        """

        FormamentisNetwork = namedtuple("FormamentisNetwork", ["edges", "vertices"])
        edges = []
        vertices = set()

        # Read the file and process each line
        with open(filepath, "r") as file:
            for line in file:
                # Split the line into two vertices
                vertex1, vertex2 = map(str.strip, line.split(","))
                # Add the edge to the edges list
                edges.append((vertex1, vertex2))
                # Add the vertices to the vertices set
                vertices.update([vertex1, vertex2])

        # Convert the vertices set to a sorted list
        vertices = sorted(vertices)

        # Create and return the FormamentisNetwork named tuple
        return FormamentisNetwork(edges=edges, vertices=vertices)

    def nxgraph_to_formamentis(self, graph):
        """
        Converts a networkx graph to a formamentis network object.
        CONSIDERS ALL EDGES AS syntactic.

        Required arguments:
        *graph*:
            A networkx graph.
        ----------
        Returns:
        *fmnt*:
            A Formamentis Network of syntactic edges.
        """

        FormamentisNetwork = namedtuple("FormamentisNetwork", ["edges", "vertices"])

        # Convert graph edges to list of tuples
        edges = list(graph.edges())
        # Convert graph vertices to list
        vertices = list(graph.nodes())
        # Create and return FormamentisNetwork namedtuple
        return FormamentisNetwork(edges=edges, vertices=vertices)

    def formamentis_to_nxgraph(self, fmnt):
        """
        Converts a Formamentis Network to a NetworkX graph.

        Required arguments:
        *fmnt*:
            A Formamentis Network.

        Returns:
        *graph*:
            A NetworkX graph.
        """

        graph = nx.Graph()
        # Add nodes from vertices
        graph.add_nodes_from(fmnt.vertices)
        # Add edges from edges
        try:
            graph.add_edges_from(fmnt.edges["syntactic"])
        except:
            graph.add_edges_from(fmnt.edges)

        return graph

    from collections import defaultdict

    def combine_formamentis(self, edgelists, weights=False):
        """
        Combine multiple formamentis networks into a single formamentis network, summing the weights of any duplicate edges if specified.

        Parameters:
        -----------
        - edgelists (list): A list of edgelists to be combined. Supports FormamentisNetwork, NetworkX Graph, and raw edgelists.
        - weights (bool): If True, includes the weights of the edges. If False, edges are treated as unweighted.

        Returns:
        -----------
        - FormamentisNetwork: A namedtuple containing 'edges' (a list of combined edges) and 'vertices' (a set of unique nodes).
        OR
        - Weighted Edgelist (list): A list of tuples representing the combined edgelist, where each tuple contains the two nodes and the weight.
        """
        if type(edgelists) != list:
            raise ValueError(
                "The argument should be a list of multiple formamentis networks."
            )

        FormamentisNetwork = namedtuple("FormamentisNetwork", ["edges", "vertices"])

        # Use a defaultdict to automatically initialize weights to 0 if needed
        weighted_edges = defaultdict(int)
        vertices = set()

        # Iterate through each edgelist
        for edgelist in edgelists:
            try:
                edgelist_to_consider = list(edgelist.edges)
            except:
                try:
                    edgelist_to_consider = edgelist["fmnt"]
                except:
                    edgelist_to_consider = edgelist

            # Iterate through each edge in the current edgelist
            for edge in edgelist_to_consider:
                node1, node2 = edge[:2]
                sorted_edge = tuple(sorted((node1, node2)))
                vertices.update(sorted_edge)  # Add nodes to vertices set
                if weights and len(edge) == 3:  # If weights are provided and required
                    weighted_edges[sorted_edge] += edge[2]
                else:  # Treat as unweighted
                    weighted_edges[sorted_edge] += 1

        # Convert the defaultdict to a list of edges, optionally including weights
        edges = [
            (node1, node2, weight) if weights else (node1, node2)
            for (node1, node2), weight in weighted_edges.items()
        ]

        if weights:
            return edges
        return FormamentisNetwork(edges=edges, vertices=list(vertices))

    def find_all_shortest_paths(self, graph, start_node, end_node):
        """
        Find all shortest paths between start_node and end_node in a graph.

        Parameters:
        -----------
        - graph (list): A raw edgelist, might include weights.
        - start_node: The starting node for the shortest paths.
        - end_node: The ending node for the shortest paths.

        Returns:
        -----------
        - result (list): A list of lists that represent all the shortest paths between the nodes.
        """

        if type(graph).__name__ == "FormamentisNetwork":
            graph = graph.edges

        G = nx.Graph()

        for edge in graph:
            # If the edge has 2 elements, it's unweighted
            # If it has 3 elements, the third is the weight, which we ignore
            u, v = edge[:2]
            G.add_edge(u, v)

        try:
            # Find all shortest paths between start_node and end_node
            all_shortest_paths = list(nx.all_shortest_paths(G, start_node, end_node))

            if not all_shortest_paths:
                return f"No path found between {start_node} and {end_node}"

            return all_shortest_paths

        except nx.NetworkXNoPath:
            return f"No path exists between {start_node} and {end_node}"
        except nx.NodeNotFound as e:
            return f"Node not found: {str(e)}"

    def get_top_quantile_shortest_paths(
        self, network, start_node, end_node, top_quantile=0.25
    ):
        """
        Returns the top quantile of shortest paths between the start_node and end_node in the given network.

        Parameters:
            network (list): A raw edgelist.
            start_node (string): The starting node of the paths.
            end_node (string): The ending node of the paths.
            top_quantile (float): The quantile of paths to keep. Defaults to 0.25.

        Returns:
            list: A list of paths (as lists of nodes) from the top quantile of the shortest paths.
        """
        all_paths = self.find_all_shortest_paths(network, start_node, end_node)

        path_weights = []
        for path in all_paths:
            weight = self.calculate_path_weight(network, path)
            path_weights.append((path, weight))

        # Sort paths by weight in descending order
        sorted_paths = sorted(path_weights, key=lambda x: x[1], reverse=True)

        # Calculate the number of paths to keep
        paths_to_keep = max(1, int(len(sorted_paths) * top_quantile))

        # Return only the paths (not the weights) from the top quantile
        return [path for path, _ in sorted_paths[:paths_to_keep]]

    def plot_mindset_stream(
        self,
        graph,
        start_node,
        end_node,
        shortest_paths=None,
        top_quantile=None,
        figsize=(12, 8),
        title=" ",
    ):
        """
        Plot the mindset stream graph.

        Parameters:
        - graph (list): A raw edgelist or a FormamentisNetwork, might include weights.
        - shortest_paths(list of lists): if None, it will compute all shortest paths between the 2 nodes.
        - start_node: The starting node for the shortest paths.
        - end_node: The ending node for the shortest paths.
        - quantile (float): The top quantile of shortest paths to keep. Defaults to None. Requires a weighted edgelist.
        - figsize (tuple): Figure size for the plot. Defaults to (12, 8).

        """
        if type(graph).__name__ == "FormamentisNetwork":
            graph = graph.edges

        if shortest_paths == None:
            shortest_paths = self.find_all_shortest_paths(graph, start_node, end_node)
        if top_quantile != None and shortest_paths == None:
            try:
                shortest_paths = self.get_top_quantile_shortest_paths(
                    graph, start_node, end_node, top_quantile=top_quantile
                )
            except:
                raise ValueError(
                    "If a quantile is set, weights should be necessary in the graph."
                )

        positive, negative, ambivalent = _valences(self.language)
        start_node = shortest_paths[0][0]
        end_node = shortest_paths[0][-1]
        G = nx.Graph()

        # Count edge frequencies
        edge_counts = {}
        for path in shortest_paths:
            for i in range(len(path) - 1):
                edge = tuple(sorted([path[i], path[i + 1]]))
                edge_counts[edge] = edge_counts.get(edge, 0) + 1

        # If the network is weighted, use the weights as edge counts
        # If not weighted, all weights will be 1
        is_weighted = len(graph[0]) == 3
        for edge in graph:
            sorted_edge = tuple(sorted([edge[0], edge[1]]))
            if sorted_edge in edge_counts:
                edge_counts[sorted_edge] = edge[2] if is_weighted else 1

        # Add edges to the graph
        for edge, count in edge_counts.items():
            G.add_edge(edge[0], edge[1], weight=count)

        # Create a layout with start_node on the left and end_node on the right
        pos = {}
        nodes = set(node for path in shortest_paths for node in path)
        x_positions = {node: 0 for node in nodes}
        x_positions[start_node] = 0
        x_positions[end_node] = 1
        for path in shortest_paths:
            for i, node in enumerate(path[1:-1], 1):
                x_positions[node] = max(x_positions[node], i / (len(path) - 1))

        # Assign y-positions with more space
        y_positions = {}
        for x in set(x_positions.values()):
            nodes_at_x = [node for node, pos in x_positions.items() if pos == x]
            for i, node in enumerate(nodes_at_x):
                y_positions[node] = (
                    i - (len(nodes_at_x) - 1) / 2
                ) * 0.2  # Increased spacing

        # Set positions
        for node in nodes:
            pos[node] = (x_positions[node], y_positions[node])

        # Adjust start and end node positions
        pos[start_node] = (0, 0)
        pos[end_node] = (1, 0)

        # Determine node colors
        node_colors = []
        for node in G.nodes():
            if node in positive:
                node_colors.append("#1f77b4")  # Blue
            elif node in negative:
                node_colors.append("#d62728")  # Red
            else:
                node_colors.append("#7f7f7f")  # Grey

        # Draw the graph
        base_size = len(G.nodes())
        plt.figure(figsize=figsize, dpi=300)

        # Draw edges with varying thickness and colors
        max_count = max(edge_counts.values())
        min_width = (1.5 if is_weighted else 3) * (
            figsize[0] / 12
        )  # Reduced minimum edge width for unweighted networks
        max_width = (16 if is_weighted else 3) * (
            figsize[0] / 12
        )  # Reduced maximum edge width for unweighted networks
        for edge, count in edge_counts.items():
            start, end = edge
            if start in positive and end in positive:
                color = "#1f77b4"  # Blue
            elif start in negative and end in negative:
                color = "#d62728"  # Red
            elif (start in positive and end in negative) or (
                start in negative and end in positive
            ):
                color = "#9467bd"  # Purple
            elif (start in positive and end not in negative) or (
                end in positive and start not in negative
            ):
                color = "#b4cad6"  # Grayish blue
            elif (start in negative and end not in negative) or (
                end in negative and start not in positive
            ):
                color = "#dc9f9e"  # Grayish red
            else:
                color = "#7f7f7f"  # Grey

            # Calculate edge width with a minimum thickness
            edge_width = min_width + (count / max_count) * (max_width - min_width)

            nx.draw_networkx_edges(
                G, pos, edgelist=[edge], width=edge_width, alpha=0.45, edge_color=color
            )
        # Draw node labels with custom bbox
        # Calculate label size
        width, height = figsize
        reference_width = 12  # Reference width for (12, 8) figure
        base_font_size = 10 - base_size * 0.07  # Original calculation
        scaled_font_size = base_font_size * (
            width / reference_width
        )  # Scale based on width ratio

        labels = nx.draw_networkx_labels(
            G, pos, font_size=scaled_font_size, font_color="white"
        )

        # Customize label backgrounds
        for node, label in labels.items():
            color = node_colors[list(G.nodes()).index(node)]
            label.set_bbox(
                dict(
                    facecolor=color,
                    edgecolor="none",
                    alpha=0.7,
                    pad=0.5,
                    boxstyle="round,pad=0.5",
                )
            )

        plt.title(title, fontsize=16, fontweight="bold")
        plt.axis("off")
        plt.tight_layout()
        plt.show()

    def calculate_path_weight(self, network, path):
        """
        Calculate the weight of a given path in the network.

        Parameters:
        - network (list): A weighted edgelist.
        - path (list): A list of nodes representing all paths.

        Returns:
        - weight (float): The total weight of the path.
        """
        weight = 0
        for i in range(len(path) - 1):
            for edge in network:
                if (edge[0] == path[i] and edge[1] == path[i + 1]) or (
                    edge[1] == path[i] and edge[0] == path[i + 1]
                ):
                    weight += edge[2]
                    break
        return weight
