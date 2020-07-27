# IPSO CLI

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Remember, a few hours of trial and error can save you several minutes of looking at the README.</p>&mdash; I Am Devloper (@iamdevloper) <a href="https://twitter.com/iamdevloper/status/1060067235316809729?ref_src=twsrc%5Etfw">November 7, 2018</a></blockquote>

IPSO CLI is a command line interface used to run pipelines created with [IPSO Phen](https://github.com/tpmp-inra/ipso_phen) on images

## Getting Started

IPSO CLI is available on GitHub [at this link ](https://github.com/tpmp-inra/ipso_cli)

### Prerequisites

You need [Python](https://www.python.org/), at least version 3.6, installed on your computer.

### Installing

- Clone the repository at this address: https://github.com/tr31zh/ipso_cli
- Move into the created folder
- Create new environment: _python -m venv env_
- Activate environment: _source ./env/bin/activate_
- Clone environment: _pip install -r requirements.txt_

## Using

All command line arguments are optional, but, they must form a understandable blob.
Python environment must be activated or in path in order for the CLI to work.

### Using a stored state

--stored-state argument with a valid stored state (built in IPSO Phen) is enough to launch the CLI. This is the preferred way to use the CLI as it reduces the number of arguments.

**Example:**

```console
(env) foo@bar:~$/ipso_cli/> python ipso_cli.py --stored-state my_stored_state.json
```

### Using separated arguments

The CLI also accepts a list of arguments to build the equivalent to a stored state. These arguments must at least have:

- **A script**: --script, path to a pipeline/script built with IPSO Phen
- **A source**: this can be either:
  - **An image**: --image, path to a source image
  - **A list of images**: --image-list, a text file containing a list of images
- **An output folder**: --output-folder, path to an output folder for the extracted data
- **A file name for the final CSV file**: --csv-file-name, a file name where the final output will be written, the path will be the output folder.

**Example:**

```console
(env) foo@bar:~$/ipso_cli/> python ipso_cli.py --image my_image.tiff --script my_script.json --output-folder a_folder --csv-file-name my_csv_file_name.csv
```

### Overrides

When using a stored state, all parameters used for separate arguments can be used as overrides.  

Other overrides include that can also be used as separated parameters :

- **Thread count override**: --thread-count, number of concurrent analysis. The default value is set to 1. Avoid setting this value over the available threads of your computer.
- **Overwrite**: --overwrite, overwrite existing partial analysis, set by default to false. When analyzing images, IPSO Phen writes every image's analysis result to a different partial file, this way if the analysis must be interrupted almost nothing is lost.

## Built With

- [OPENCV](https://pypi.org/project/opencv-python//) - Image processing library.
- [Scikit image](https://scikit-image.org/) - Image processing library.
- [Numpy](https://numpy.org/) - The fundamental package for scientific computing with Python

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Authors

- **Felicià MAVIANE** - [tr31zh](https://github.com/tr31zh)

## License

This project is licensed under the MIT License - see the [LICENSE](<[LICENSE.md](https://github.com/tpmp-inra/ipso_cli/blob/master/LICENSE)>) file for details.
