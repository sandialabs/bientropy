'''
Copyright 2018 National Technology & Engineering Solutions of Sandia, LLC
(NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
Government retains certain rights in this software.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

---

This file is for creating the performance plot.
'''

import pandas
import matplotlib.pyplot as plt

times = pandas.read_csv('bientropy_times.csv', index_col=0)

times.plot(logy=True, logx=True)
plt.ylabel('Time (s)')
plt.grid(b=True, which='major')
plt.grid(b=True, which='minor', linestyle=':')
plt.show()
