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
from collections import defaultdict
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
from collections import namedtuple
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
        """

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
                save_path=save_path,
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
        graph.add_edges_from(fmnt.edges)
        return graph

    from collections import defaultdict

    def combine_edgelists(self, edgelists):
        """
        Combine multiple edgelists into a single edgelist, summing the weights of any duplicate edges.
        Parameters:
        -----------
        - edgelists (list): A list of edgelists to be combined. Supports FormamentisNetwork, NetworkX Graph and raw edgelists.
        Returns:
        -----------
        - result (list): A list of tuples representing the combined edgelist, where each tuple contains the two nodes and the weight.
        """
        if type(edgelists) != list:
            raise ValueError("The argument should be a list of formamentis networks.")

        # Use a defaultdict to automatically initialize weights to 0
        weighted_edges = defaultdict(int)
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
                sorted_edge = tuple(sorted(edge[:2]))
                weighted_edges[sorted_edge] += 1
        # Convert the defaultdict to a list of tuples (node1, node2, weight)
        result = [
            (edgelist_to_consider[0], edgelist_to_consider[1], weight)
            for edgelist_to_consider, weight in weighted_edges.items()
        ]
        return result

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

    def plot_mindset_stream(self, network, shortest_paths=None, start_node, end_node):
        """
        Plot the mindset stream graph.

        Parameters:
        - graph (list): A raw edgelist, might include weights.
        - shortest_paths(list of lists): if None, it will compute all shortest paths between the 2 nodes.
        - start_node: The starting node for the shortest paths.
        - end_node: The ending node for the shortest paths.

        """
        if shortest_paths==None:
            all_shortest_paths = self.find_all_shortest_paths(network, start_node, end_node)
        positive, negative, ambivalent = _valences("english")
        start_node = all_shortest_paths[0][0]
        end_node = all_shortest_paths[0][-1]
        G = nx.Graph()

        # Count edge frequencies
        edge_counts = {}
        for path in all_shortest_paths:
            for i in range(len(path) - 1):
                edge = tuple(sorted([path[i], path[i + 1]]))
                edge_counts[edge] = edge_counts.get(edge, 0) + 1

        # If the network is weighted, use the weights as edge counts
        if len(network[0]) == 3:
            for edge in network:
                sorted_edge = tuple(sorted([edge[0], edge[1]]))
                if sorted_edge in edge_counts:
                    edge_counts[sorted_edge] = edge[2]

        # Add edges to the graph
        for edge, count in edge_counts.items():
            G.add_edge(edge[0], edge[1], weight=count)

        # Create a layout with start_node on the left and end_node on the right
        pos = {}
        nodes = set(node for path in all_shortest_paths for node in path)
        x_positions = {node: 0 for node in nodes}
        x_positions[start_node] = 0
        x_positions[end_node] = 1
        for path in all_shortest_paths:
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
        plt.figure(figsize=(12, 8), dpi=300)
        # nx.draw_networkx_nodes(G, pos, node_size=3500, node_color=node_colors, alpha=0.8, linewidths=2, edgecolors='white')
        # nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')

        # Draw edges with varying thickness and colors
        max_count = max(edge_counts.values())

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

            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=[edge],
                width=(count / max_count) * 16,
                alpha=0.5,
                edge_color=color,
            )

        # Create rounded rectangular backgrounds for node labels
        for node, (x, y) in pos.items():
            color = node_colors[list(G.nodes()).index(node)]
            rect_width = 0.11 - base_size * 0.0035
            rect_height = base_size * 0.002
            scaled_font_size = 14 - base_size * 0.07

            dynamic_pad = rect_height * 1.01 + base_size * 0.0005

            rect = patches.FancyBboxPatch(
                (x - rect_width / 2, y - rect_height / 2),
                rect_width,
                rect_height,
                boxstyle=f"round,pad={dynamic_pad}",
                linewidth=0,
                facecolor=color,
                edgecolor="none",
                alpha=0.9,
                zorder=2,
                transform=plt.gca().transData,
            )
            plt.gca().add_patch(rect)

        # Draw node labels
        nx.draw_networkx_labels(G, pos, font_size=scaled_font_size, font_color="white")

        plt.title("Mindset Stream", fontsize=16, fontweight="bold")
        plt.axis("off")
        plt.tight_layout()
        plt.show()
