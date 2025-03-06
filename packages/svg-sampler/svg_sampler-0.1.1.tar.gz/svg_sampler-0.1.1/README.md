# SVGSampler
This is a small project to quickly create 2D multiclass-datasets for machine learning applications.

You can install it using pip:

```
pip install svg_sampler
```

Then you can use the function `sample_from_svg` to sample datapoints from the filled in paths/objects of the svg.

# Example:

![image](examples/test.svg)

```python
from svg_sampler import sample_from_svg
from matplotlib import pyplot as plt

X, y = sample_from_svg("test.svg", 5000, normalize=True, sample_setting="based_on_area", overlap_mode="upper_only")
plt.scatter(X[:, 0], X[:, 1], c=y)
plt.show()
```
![image](examples/sampled.svg)
