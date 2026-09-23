#!/bin/sh
# r = 0.6 is past the explicit scheme's stability limit: the peak grows instead of shrinking.
$LZ run --scheme=ftcs --r=0.6 --t=0.2
$LZ run --scheme=cn --r=5
