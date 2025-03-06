### temporal-lib
A library for working with datetime and other temporal concepts.

### Explanation
Originally, I created a "Temporal" [companion App](https://github.com/Datahenge/temporal) for the [Frappe Framework](https://frappeframework.com/).
Over time, more of my non-ERPNext Python projects required or benefitted from the same helper functions and classes.

So I'm splitting the project:
* All generic, reusable Python code will be stored in this package, and synchronized to PyPi.org.
* The remaining Frappe-specific code will remain on GitHub, and begin to reference this package as a requirement.

### Installation
```bash
pip3 install temporal-lib
```

### Usage
The library's namespace is `temporal_lib`.  For example:

```python
""" your_code.py """
from datetime import datetime
import temporal_lib

today_date = datetime.now().date()
today_iso_string = temporal_lib.date_to_iso_string(today)
print(today_iso_string)
```
----

### Standards

* All date strings are expected to be ISO-8601 extended.  Example: 2023-11-29

### Links
* To the `temporal-lib` package on PyPi [here](https://pypi.org/project/temporal-lib/).
* A helpful [Wikipedia article](https://en.wikipedia.org/wiki/ISO_8601) about ISO-8601.
* To my **Rust**-based `file-8601` project [here](https://gitlab.com/brian_pond/file8601_rust)!
* (Deprecated) My original Python `file-8601` project [here](https://gitlab.com/brian_pond/file8601)

### Further Reading
* https://blog.ganssle.io/articles/2018/03/pytz-fastest-footgun.html
* https://blog.ganssle.io/articles/2018/02/aware-datetime-arithmetic.html
* https://github.com/regebro/tzlocal/issues/90#issuecomment-699714858
* https://github.com/dateutil/dateutil


### Attributions
Hourglass image on GitLab repository by The Oxygen Team, KDE; - KDE github;, LGPL, https://commons.wikimedia.org/w/index.php?curid=18609110
