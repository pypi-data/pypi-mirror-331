import os
from typing import List, Union

import gdown
import torch

import bkit
from bkit.pos import Infer as PosInfer
from bkit.shallow._models import decoder
from bkit.utils import MODEL_URL_MAP

from IPython.display import HTML
import json
from nltk import Tree


def visualize(prediction):
    """
    Creates an interactive visualization of a constituency parse tree from a prediction string.
    Displays the tree from top to bottom.
    Args:
        prediction (str): The constituency parsing prediction in bracket notation
    Returns:
        IPython.display.HTML: Interactive HTML visualization of the tree
    """

    def bracket_to_dict(tree):
        """Convert bracket notation to dictionary format for D3.js"""
        if isinstance(tree, str):
            return {"name": tree}
        return {
            "name": tree.label(),
            "children": [bracket_to_dict(child) for child in tree]
        }
    # Convert prediction to Tree object
    tree = Tree.fromstring(prediction)
    # Convert to dictionary format for D3
    tree_dict = bracket_to_dict(tree)
    # HTML template with D3.js visualization
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
    body {
        margin: 0;
        padding: 0;
    }

    #tree-container {
        width: 80%;  /* Set a percentage width for responsiveness */
        max-width: 1200px;  /* Maximum width to avoid stretching on large screens */
        height: 600px;  /* Increased height for vertical layout */
        background-color: white;
        overflow: auto;
        padding: 20px;
        box-sizing: border-box;
        border-radius: 8px;  /* Optional: rounded corners for aesthetic */
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);  /* Slight shadow for depth */
    }

    .node circle {
        fill: #fff;
        stroke: #4a90e2;
        stroke-width: 2.5px;
    }

    .node text {
        font: 14px Arial;
        color: #333;
    }

    .node:hover circle {
        stroke: #2ecc71;
        stroke-width: 3px;
    }

    .link {
        fill: none;
        stroke: #bdc3c7;
        stroke-width: 2px;
    }

    svg {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>

    </head>
    <body>
        <div id="tree-container">
            <div style="text-align: center; margin-bottom: 10px; font-family: Arial; color: #333;">
                <h3>Shallow Parsing Tree</h3>
            </div>
        </div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.17/d3.min.js"></script>
        <script>
            var treeData = TREE_DATA_PLACEHOLDER;
            var margin = {top: 40, right: 20, bottom: 20, left: 20},
                width = 960 - margin.right - margin.left,
                height = 800 - margin.top - margin.bottom;
            var i = 0;
            var duration = 750;
            var root;
            var tree = d3.layout.tree()
                .size([width, height]);
            var diagonal = d3.svg.diagonal()
                .projection(function(d) { return [d.x, d.y]; });  // Swapped x and y for vertical layout
            var svg = d3.select("#tree-container").append("svg")
                .attr("width", width + margin.right + margin.left)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
            root = treeData;
            root.x0 = width / 2;
            root.y0 = 0;
            update(root);
            function update(source) {
                var nodes = tree.nodes(root).reverse(),
                    links = tree.links(nodes);
                // Normalize for fixed-depth
                nodes.forEach(function(d) { d.y = d.depth * 100; });  // Reduced vertical spacing
                var node = svg.selectAll("g.node")
                    .data(nodes, function(d) { return d.id || (d.id = ++i); });
                var nodeEnter = node.enter().append("g")
                    .attr("class", "node")
                    .attr("transform", function(d) {
                        return "translate(" + source.x0 + "," + source.y0 + ")";
                    });
                nodeEnter.append("circle")
                    .attr("r", 1e-6)
                    .style("fill", "#fff");
                nodeEnter.append("text")
                    .attr("y", function(d) {
                        return d.children || d._children ? -20 : 20;
                    })
                    .attr("dy", ".35em")
                    .attr("text-anchor", "middle")  // Center text
                    .text(function(d) { return d.name; })
                    .style("fill-opacity", 1e-6);
                var nodeUpdate = node.transition()
                    .duration(duration)
                    .attr("transform", function(d) {
                        return "translate(" + d.x + "," + d.y + ")";
                    });
                nodeUpdate.select("circle")
                    .attr("r", 8)
                    .style("fill", "#fff");
                nodeUpdate.select("text")
                    .style("fill-opacity", 1);
                var nodeExit = node.exit().transition()
                    .duration(duration)
                    .attr("transform", function(d) {
                        return "translate(" + source.x + "," + source.y + ")";
                    })
                    .remove();
                nodeExit.select("circle")
                    .attr("r", 1e-6);
                nodeExit.select("text")
                    .style("fill-opacity", 1e-6);
                var link = svg.selectAll("path.link")
                    .data(links, function(d) { return d.target.id; });
                link.enter().insert("path", "g")
                    .attr("class", "link")
                    .attr("d", function(d) {
                        var o = {x: source.x0, y: source.y0};
                        return diagonal({source: o, target: o});
                    });
                link.transition()
                    .duration(duration)
                    .attr("d", diagonal);
                link.exit().transition()
                    .duration(duration)
                    .attr("d", function(d) {
                        var o = {x: source.x, y: source.y};
                        return diagonal({source: o, target: o});
                    })
                    .remove();
                nodes.forEach(function(d) {
                    d.x0 = d.x;
                    d.y0 = d.y;
                });
            }
        </script>
    </body>
    </html>
    """
    # Replace placeholder with actual tree data
    html_content = html_template.replace(
        'var treeData = TREE_DATA_PLACEHOLDER;',
        f'var treeData = {json.dumps(tree_dict, ensure_ascii=False)};'
    )
    return display(HTML(html_content))




def get_model_object():
    """
    Download and load the pre-trained model.

    Returns:
        model_object: Loaded pre-trained model.
    """
    url = MODEL_URL_MAP["shallow"]
    cache_dir = bkit.ML_MODELS_CACHE_DIR
    model_path = os.path.join(cache_dir, "shallow_model.pt")

    # Create the cache directory if it doesn't exist
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    # Download the model if it doesn't exist in the cache
    if not os.path.exists(model_path):
        gdown.download(url, model_path, quiet=False, fuzzy=True)

    # Load the model using torch_load from utils
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_object = torch.load(model_path, map_location=device)

    return model_object


class Infer(object):
    def __init__(self, pos_model: str = "pos-noisy-label", batch_size: int = 1):
        """
        Initialize a ShallowInference instance.

        Args:
            batch_size (int, optional): The batch size for inference. Defaults to 1.
        """

        # Obtain the pre-trained model object
        self.model_object = get_model_object()

        # Extract model specifications and state dictionary
        self.model_spec = self.model_object["spec"]
        self.model_state_dict = self.model_object["state_dict"]

        # Create a chart parser model using the specifications and state dictionary
        self.model = decoder.ChartParser.from_spec(
            self.model_spec, self.model_state_dict
        )

        # Initialize a part-of-speech tagging model
        self.pos_model = PosInfer(pos_model)

        # Set the batch size for inference
        self.batch_size = batch_size

    def __call__(self, text: Union[str, List[str]]) -> Union[str, List[str]]:
        """
        Perform shallow inference on the provided input text or list of texts.

        Args:
            text (Union[str, List[str]]): Input text or list of texts for shallow inference.

        Returns:
            Union[str, List[str]]: Inference results as a single string or a list of strings.
        """

        # Get sentences and corresponding part-of-speech tags for the input text
        sentences, tags = self.get_sentences_with_tags(text)

        all_predicted = []
        for start_index in range(0, len(sentences), self.batch_size):
            subbatch_sentences = sentences[start_index : start_index + self.batch_size]

            subbatch_tags = tags[start_index : start_index + self.batch_size]
            subbatch_sentences = [
                [(tag, word) for tag, word in zip(taag, sentence)]
                for taag, sentence in zip(subbatch_tags, subbatch_sentences)
            ]

            predicted, _ = self.model.parse_batch(subbatch_sentences)
            del _

            all_predicted.extend([p.convert() for p in predicted])

        if len(all_predicted) == 1:
            return all_predicted[0].linearize()
        else:
            return [predicted.linearize() for predicted in all_predicted]

    def get_pos_tag(self, sentence):
        """
        Perform part-of-speech tagging on a sentence and return the list of POS tags.

        Args:
            sentence (str): Input sentence for part-of-speech tagging.

        Returns:
            List[str]: List of part-of-speech tags for words in the sentence.
        """
        pos_tagger_results = self.pos_model(sentence)

        poses = []
        for word, pos, confidence in pos_tagger_results:
            poses.append(pos)
        return poses

    def get_sentences_with_tags(
        self, text: Union[str, List[str]]
    ) -> Union[str, List[str]]:
        """
        Tokenize input text or list of texts and perform part-of-speech tagging on each sentence.

        Args:
            text (Union[str, List[str]]): Input text or list of texts.

        Returns:
            Tuple[List[List[str]], List[List[str]]]: Lists of tokenized sentences and their corresponding POS tags.
        """
        if isinstance(text, str):
            raw_sentences = [text]

        elif isinstance(text, list):
            raw_sentences = text

        else:
            raise ValueError("Invalid input! \n Give a string or a list of strings.")

        sentences = []
        tags = []
        for sentence in raw_sentences:
            sentences.append(bkit.tokenizer.tokenize(sentence))
            tags.append(self.get_pos_tag(sentence))

        return sentences, tags
