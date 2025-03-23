# deepfake-project

This repository is the parent repository gathering all the work carried out during an ENSTA project on deepfake generation, with a particular focus on face swaps.

The group members who actively participated in the project are as follows:

- Isabelle NEVEU (https://github.com/Isabelle-ensta)
- Julian FIDELIN-DURAND (https://github.com/Barbossa972)
- Thomas BONNET (https://github.com/GroBonnet)
- Tao GUINOT (https://github.com/taognt)
- Florian MOREL (https://github.com/florian-morel22)

# Setup

In order to retrieve all the sub-repositories that make up this project, please run the following command at the root of the repository:

```
make clone
```

Next, to set up the sub-repositories required for the demo to work, please run the following command:

```
make setup
```

# Run Demo

To run the demo, please run the following command to run the client side :

```
make demo-run-client
```

and the following command to run the server side :

```
make demo-run-server
```

⚠️ The server side must be run on a GPU-equipped machine !
