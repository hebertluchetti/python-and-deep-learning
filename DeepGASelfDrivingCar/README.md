# Deep-GA-Self-Driving-Car V1.0
## Self Driving Car in Python using Genetic Algorithm and Neural Networks by Deep Reinforcement Learning

This is a study project I created to learn the basics of reinforcement learning neural network and 
genetic algorithms. This simulation was implemented using Python libraries: Pyglet, Pymunk, Pytorch. 
The 2D simulation employs an unsupervised reinforcement learning algorithm in which virtual cars need to find 
the best way to travel the track on their own. This track has limits that guide how cars should drive on their own.

The basic idea is to use Genetic Algorithm to find the best weights of a Neural Network (in Pytorch) which outperforms 
the traditional advanced reinforcement learning algorithms in learning how to drive a virtual car. I created a car race 
simulation using Pymunk and Pyglet in which a car needs to drive itself following a track. 
I used the following studies as references: 
[Deep reinforcement learning using genetic algorithm for parameter optimization] (https://arxiv.org/pdf/1905.04100.pdf) 
and from Uber AI Labs
[Deep neuroevolution: genetic algorithms are a competitive alternative for training deep neural networks for reinforcement learning] (https://arxiv.org/abs/1712.06567)

The application starts creating 10 cars in each generation and assigned random neural networks to each one of them and 
then it set the rewards based on the distance it travels without colliding with the track.
This reward is used to rank neural networks from worst to best. Therefore, in each generation, the Genetic Algorithm 
develops the Neural Networks and we obtain new model slightly better than the previous generation. 
The best model for each generation is saved in a file and the information is saved also in the `best_model.ini` file. 
So we can start a new process with a different track shape using this best model.

The application allows you to draw the track that will be used in the simulation of the models and vertices of 
the track are registered in the `track.ini` file. Thus, at each startup of the application, the user has the possibility 
to use the last created track.
For running the application is needed run the `car_simulation_win.py` script.

## Dependencies
```bash
- Pymunk
- Pyglet
- Pytorch
- Configparser
- Shapely
```

## Genetic Algorithm and Neural Networks
Genetic Algorithm combined with Neural Networks examples.

- Intelligent Flappy Bird (Genetic-Algorithm-And-Neural-Networks/Intelligent_Flappy_Bird/)
  - Video: [A.I. Learns to Play Flappy-Bird](https://www.youtube.com/watch?v=H9BY-xr2QBY)
  - More Information: [A.I. Learns to Play Flappy-Bird](https://jatinmandav.wordpress.com/2018/03/05/a-i-learns-to-play-flappy-bird/)
- Self-Driving Cars (Genetic-Algorithm-And-Neural-Networks/Self-Driving-Cars/)
  - Video: [Car/A.I. Learns to Drive](https://www.youtube.com/watch?v=_TGGbPjT7pg)
  - More Information: [A.I. Learns to Drive](https://jatinmandav.wordpress.com/2018/03/09/a-i-learns-to-drive)

##Contact: Hebert Luchetti Ribeiro
```bash
Rua Horácio Pessini 330, ap.32 – Nova Aliança, 
CEP 14026-590, Ribeirão Preto – S.P. - Brazil

mobile: +55 (16) 99796-7399
email: hebert.luchetti@gmail.com
linkedin: https://www.linkedin.com/in/hebert-luchetti-ribeiro-aa42923
youtube:https://www.youtube.com/channel/UCf0w-raMzq6rNxxjNJ7D1gQ
```
