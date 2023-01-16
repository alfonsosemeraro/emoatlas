import unittest
from emoatlas import EmoScores


class EmoAtlasTestCase(unittest.TestCase):
    def test_zscores(self):
        emos = EmoScores()
        sample_text = """In this text, we prefer dogs becase they are happy and dogs are positive.
        Good dogs make good friends. Cats however are bad and have negative links. We dislike cats."""
        fmnt = emos.formamentis_network(sample_text)
        bag_of_words_dog = " ".join(
            [pair[1] for pair in fmnt.edges if pair[0].lower() == "dog"]
        )
        zscores = emos.zscores(bag_of_words_dog)
        self.assertListEqual(
            list(zscores.keys()),
            [
                "anger",
                "trust",
                "surprise",
                "disgust",
                "joy",
                "sadness",
                "fear",
                "anticipation",
            ],
        )


if __name__ == "__main__":
    unittest.main()
