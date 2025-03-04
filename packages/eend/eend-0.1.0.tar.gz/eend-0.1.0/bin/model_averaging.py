# eend/bin/model_averaging.py
#!/usr/bin/env python3

# Copyright 2019 Hitachi, Ltd. (author: Yusuke Fujita)
# Licensed under the MIT license.

import argparse
import numpy as np


def average_model_chainer(ifiles, ofile):
    """Average multiple Chainer models.
    
    Args:
        ifiles: List of input model files
        ofile: Output averaged model file
    """
    omodel = {}
    # get keys from the first file
    model = np.load(ifiles[0])
    for x in model:
        if 'model' in x:
            print(x)
    keys = [x.split('main/')[1] for x in model if 'model' in x]
    print(keys)
    for path in ifiles:
        model = np.load(path)
        for key in keys:
            val = model['updater/model:main/{}'.format(key)]
            if key not in omodel:
                omodel[key] = val
            else:
                omodel[key] += val
    for key in keys:
        omodel[key] /= len(ifiles)
    np.savez_compressed(ofile, **omodel)


def parse_arguments():
    """Parse command line arguments for model_averaging script."""
    parser = argparse.ArgumentParser(description='Average multiple models')
    parser.add_argument('ofile', help='Output model file')
    parser.add_argument('ifiles', nargs='+', help='Input model files')
    parser.add_argument('--backend', default='chainer',
                        choices=['chainer', 'pytorch'],
                        help='Backend framework')
    return parser.parse_args()


def main():
    """Main function for model_averaging script."""
    args = parse_arguments()
    
    if args.backend == 'chainer':
        average_model_chainer(args.ifiles, args.ofile)
    elif args.backend == 'pytorch':
        # TODO: Implement PyTorch model averaging
        raise NotImplementedError("PyTorch model averaging is not implemented yet")
    else:
        raise ValueError(f"Unsupported backend: {args.backend}")
    
    print(f"Averaged model saved to {args.ofile}")


if __name__ == "__main__":
    main()

