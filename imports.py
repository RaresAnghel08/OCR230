import os
import shutil
from PIL import Image
import easyocr
import numpy as np
import re
import sys

from src.processing.coordonate import coordonate
from src.processing.filtre import *
