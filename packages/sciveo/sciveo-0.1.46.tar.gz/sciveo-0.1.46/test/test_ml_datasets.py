#
# Pavlin Georgiev, Softel Labs
#
# This is a proprietary file and may not be copied,
# distributed, or modified without express permission
# from the owner. For licensing inquiries, please
# contact pavlin@softel.bg.
#
# 2024
#

import unittest
import json

from sciveo.ml.dataset.object_detection import *


class TestMLDatasets(unittest.TestCase):
  def test_object_detection(self):
    HOME_PATH = os.path.expanduser("~")

    ds = YOLODataset()
    ds.load(f"{HOME_PATH}/data/test_yolo")
    debug("classes", ds.classes)
    ds.save(f"{HOME_PATH}/data/tmp/yolo-out", classes=["block", "vertical"], copy_images=True)

    ds = ObjectDetectionDataset()
    ds.from_yolo(f"{HOME_PATH}/data/test_yolo")
    stats = ds.stats()
    debug("stats", stats)
    info("distribution", stats["distribution"])
    ds.save(f"{HOME_PATH}/data/tmp/od-1", copy_images=False)


if __name__ == '__main__':
  unittest.main()
