# Copyright (C) 2023 Jahanzeb Ahmed
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# AutoxEDA any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# For Guidance reach me out through email jahanzebahmed.mail@gmail.com, or through my website <https://jahanzebahemd.netlify.app/>

import pytest
from autoxeda.core import autoeda
import pandas as pd

def test_autoeda():
    np.random.seed(42) # Randomized Seed for Random generation...
    data = {"x": np.random.normal(0, 1, 1000), "y": np.random.normal(0, 1, 1000)} # Normalized Distribution (i.e: Mean=0, SD=1)
    df = pd.DataFrame(data) # Finalized DataFrame
    result = autoeda(df, analysis_type="business", api_key=None, temperature = 0.3) # Main function (autoeda).
    assert isinstance(result, dict)
