from SAES.plots.Pplot import Pplot
from PIL import Image
import unittest, os

class TestBoxplot(unittest.TestCase):
    
    def setUp(self):
        swarmIntelligence = "tests/test_data/swarmIntelligence.csv"
        multiobjectiveMetrics = "tests/test_data/multiobjectiveMetrics.csv"
        metric = "HV"
        self.pplot = Pplot(swarmIntelligence, multiobjectiveMetrics, metric)

    def test_save(self):
        self.pplot.save("NSGAII", "OMOPSO", f"{os.getcwd()}/tests/plots", file_name="pplot.png", width=10)
        image_path = f"{os.getcwd()}/tests/plots/pplot.png"
        self.assertTrue(os.path.exists(image_path))

        # Open the image and check its size
        with Image.open(image_path) as img:
            width, height = img.size
            self.assertEqual((width, height), (1019, 1019))

        os.remove(image_path)
    
    def test_save_pivot(self):
        self.pplot.save_pivot("NSGAII", f"{os.getcwd()}/tests/plots")
        image_path = f"{os.getcwd()}/tests/plots/pivot_NSGAII.png"
        self.assertTrue(os.path.exists(image_path))

        # Open the image and check its size
        with Image.open(image_path) as img:
            width, height = img.size
            self.assertEqual((width, height), (1768, 989))

        os.remove(image_path)

    def test_show(self):
        self.pplot.show("NSGAII", "OMOPSO")
        self.assertTrue(True)

    def test_show_pivot(self):
        self.pplot.show_pivot("NSGAII")
        self.assertTrue(True)
