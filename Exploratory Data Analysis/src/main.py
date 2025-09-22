import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import config
from statistical_analysis import NetflixEda


if __name__ == "__main__":
    eda = NetflixEda()
    eda.run_complete_analysis()