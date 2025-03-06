# this is a hot fix for an apparent issue on our Jess cluster
# fix found here:
# https://stackoverflow.com/questions/52026652/openblas-blas-thread-init-pthread-create-resource-temporarily-unavailable
import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
