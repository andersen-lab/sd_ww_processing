#!/bin/bash

eval "$(mamba shell hook --shell bash)"
mamba activate freyja
exec ./demix_parallel_ubuntu.sh
