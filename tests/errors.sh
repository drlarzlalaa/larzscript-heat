#!/bin/sh
$LZ run --scheme=implicit
$LZ run --r=0
$LZ run --r=200
$LZ run --t=0
$LZ run --t=20
$LZ run --r=0.01 --t=5
$LZ run --r=0.4 --t=0.001
$LZ run --r=abc
