import os
import shutil
from PIL import Image
import easyocr
import numpy as np
from coordonate import coordonate
from filtre import *
from process import proceseaza_fisier, proceseaza_zona
from folders import *
from openai import OpenAI
# from generare_adresa import corecteaza_adresa
import re
import sys