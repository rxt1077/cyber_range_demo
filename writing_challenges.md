# Writing Challenges

Challenges are defined in a `challenge.py` file located in a separate directory in `challenges/`.
You can see five examples in this repo: `challenges/challenge1`, `challenges/challenge2`, `challenges/challenge3`, `challenges/challenge4`, and `challenges/challenge5`.

In order to make a new challenge:

0. Make a new directory in `challenges`
0. Make a new `challenge.py` in that directory that follows the conventions shown in the examples
0. Import your new challenge at the top of `challenges/routes.py`
0. Add your new import to the the `AVAILABLE_CHALLENGES` list at the top of `challenges/routes.py`

You will need to make sure that any Docker images you want to use are built on the system, see `build_images.sh`, and that any templates you use have a unique name and are stored in `challenges/templates`.
