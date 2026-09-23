#!/bin/sh
# A stable step (r <= 1/2) reproduces the exact Gaussian; the variance is exactly 2Dt.
$LZ run
$LZ run --scheme=ftcs --r=0.25 --t=0.5
$LZ run --scheme=cn --r=1 --t=2
