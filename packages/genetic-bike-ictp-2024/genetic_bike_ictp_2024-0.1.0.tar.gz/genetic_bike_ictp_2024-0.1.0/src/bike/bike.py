"""
Module for simulating a bike with two wheels and two body nodes connected by Hookean springs with damping factors.
Classes
Bike
    A class to represent a bike with two wheels and two body nodes, all connected by springs with damping factors.
    Generate any bike with two wheels, two body nodes, all connected by Hookean spring with a damping factor. Here:
            The coordinates of the wheels and body nodes.
        spring coefficients : array, shape = (4, 4)
            The spring coefficients between the nodes.
        loss coefficients : array, shape = (4, 4)
            The loss coefficients between the nodes.
        Get the torque values of the wheels.
        torques : list
            The torque values of the wheels.
        Get the radii of the wheels.
        radius : list
            The radii of the wheels.
        node_i : int
            Index of the first node.
        node_j : int
            Index of the second node.
            The length of the spring between the two nodes.
            The lengths of all the springs between the nodes.
            The masses of the wheels and body nodes.
"""

import numpy as np


class Bike:
    """
    Generate any bike with
    two wheels, two body nodes, all connected by
    Hookean spring with a damping factor. Here:
    w1 ~ wheel_1
    w2 ~ wheel_2
    b1 ~ body_1
    b2 ~ body_2

    Parameters
    ----------
    wheel_1_x : float
        x coordinate of the first wheel.
    wheel_1_y : float
        y coordinate of the first wheel.
    wheel_1_radius: float
        first wheel radius
    wheel_1_mass: float
        first wheel mass
    wheel_1_torque: float
        first wheel torque

    wheel_2_x : float
        x coordinate of the first wheel.
    wheel_2_y : float
        y coordinate of the first wheel.
    wheel_2_radius: float
        first wheel radius
    wheel_2_mass: float
        first wheel mass
    wheel_2_torque: float
        first wheel torque

    body_1_x: float
        x coordinate of the first body node
    body_1_y: float
        y coordinate of the first body node
    body_1_mass: float
        mass of the first body node

    body_2_x: float
        x coordinate of the first body node
    body_2_y: float
        y coordinate of the first body node
    body_2_mass: float
        mass of the first body node

    k_spring_w1_w2: float
        spring coefficient of the spring 1, connecting wheel 1 and wheel 2
    k_spring_w1_b1: float
        spring coefficient of the spring 2, connecting wheel 1 and body 1
    k_spring_w1_b2: float
        spring coefficient of the spring 3, connecting wheel 1 and body 2
    k_spring_w2_b1: float
        spring coefficient of the spring 4, connecting wheel 2 and body 1
    k_spring_w2_b2: float
        spring coefficient of the spring 5, connecting wheel 2 and body 2
    k_spring_b1_b2: float
        spring coefficient of the spring 6, connecting body 1 and body 2

    loss_spring_w1_w2: float
        loss coefficient of the spring 1, connecting wheel 1 and wheel 2
    loss_spring_w1_b1: float
        loss coefficient of the spring 2, connecting wheel 1 and body 1
    loss_spring_w1_b2: float
        loss coefficient of the spring 3, connecting wheel 1 and body 2
    loss_spring_w2_b1: float
        loss coefficient of the spring 4, connecting wheel 2 and body 1
    loss_spring_w2_b2: float
        loss coefficient of the spring 5, connecting wheel 2 and body 2
    loss_spring_b1_b2: float
        loss coefficient of the spring 6, connecting body 1 and body 2

    Returns
    -------
    class
        a bike as a class

    """

    def __init__(
        self,
        wheel_1_x,
        wheel_1_y,
        wheel_1_radius,
        wheel_1_mass,
        wheel_1_torque,
        wheel_2_x,
        wheel_2_y,
        wheel_2_radius,
        wheel_2_mass,
        wheel_2_torque,
        body_1_x,
        body_1_y,
        body_1_mass,
        body_2_x,
        body_2_y,
        body_2_mass,
        k_spring_w1_w2,
        k_spring_w1_b1,
        k_spring_w1_b2,
        k_spring_w2_b1,
        k_spring_w2_b2,
        k_spring_b1_b2,
        loss_spring_w1_w2,
        loss_spring_w1_b1,
        loss_spring_w1_b2,
        loss_spring_w2_b1,
        loss_spring_w2_b2,
        loss_spring_b1_b2,
    ):

        self.wheel_1_x = wheel_1_x
        self.wheel_1_y = wheel_1_y
        self.wheel_1_radius = wheel_1_radius
        self.wheel_1_mass = wheel_1_mass
        self.wheel_1_torque = wheel_1_torque

        self.wheel_2_x = wheel_2_x
        self.wheel_2_y = wheel_2_y
        self.wheel_2_radius = wheel_2_radius
        self.wheel_2_mass = wheel_2_mass
        self.wheel_2_torque = wheel_2_torque

        self.body_1_x = body_1_x
        self.body_1_y = body_1_y
        self.body_1_mass = body_1_mass

        self.body_2_x = body_2_x
        self.body_2_y = body_2_y
        self.body_2_mass = body_2_mass

        self.k_spring_w1_w2 = k_spring_w1_w2
        self.k_spring_w1_b1 = k_spring_w1_b1
        self.k_spring_w1_b2 = k_spring_w1_b2
        self.k_spring_w2_b1 = k_spring_w2_b1
        self.k_spring_w2_b2 = k_spring_w2_b2
        self.k_spring_b1_b2 = k_spring_b1_b2

        self.loss_spring_w1_w2 = loss_spring_w1_w2
        self.loss_spring_w1_b1 = loss_spring_w1_b1
        self.loss_spring_w1_b2 = loss_spring_w1_b2
        self.loss_spring_w2_b1 = loss_spring_w2_b1
        self.loss_spring_w2_b2 = loss_spring_w2_b2
        self.loss_spring_b1_b2 = loss_spring_b1_b2

    def get_coordinates(self):
        """
        Get the coordinates of wheel 1, wheel 2, body 1, body 2

        Return
        ----------
            coordinates : array, shape = (6, 2)

        """

        nodes_coordinates = np.array(
            [
                [self.wheel_1_x, self.wheel_1_y],
                [self.wheel_2_x, self.wheel_2_y],
                [self.body_1_x, self.body_1_y],
                [self.body_2_x, self.body_2_y],
            ]
        )

        return nodes_coordinates

    def get_springs_k(self):
        """
        Get the spring coefficients.

        Return
        ----------
            spring coeffcients : array, shape = (4, 4)

        """

        springs_k = np.array(
            [
                [0, self.k_spring_w1_w2, self.k_spring_w1_b1, self.k_spring_w1_b2],
                [self.k_spring_w1_w2, 0, self.k_spring_w2_b1, self.k_spring_w2_b2],
                [self.k_spring_w1_b1, self.k_spring_w2_b1, 0, self.k_spring_b1_b2],
                [self.k_spring_w1_b2, self.k_spring_w2_b2, self.k_spring_b1_b2, 0],
            ]
        )

        return springs_k

    def get_springs_loss(self):
        """
        Get the loss coefficients.

        Return
        ----------
            loss coeffcients : array, shape = (4, 4)

        """

        springs_loss = np.array(
            [
                [
                    0,
                    self.loss_spring_w1_w2,
                    self.loss_spring_w1_b1,
                    self.loss_spring_w1_b2,
                ],
                [
                    self.loss_spring_w1_w2,
                    0,
                    self.loss_spring_w2_b1,
                    self.loss_spring_w2_b2,
                ],
                [
                    self.loss_spring_w1_b1,
                    self.loss_spring_w2_b1,
                    0,
                    self.loss_spring_b1_b2,
                ],
                [
                    self.loss_spring_w1_b2,
                    self.loss_spring_w2_b2,
                    self.loss_spring_b1_b2,
                    0,
                ],
            ]
        )

        return springs_loss

    def get_torques(self):
        """
        Get the torque values of the wheels

        Return
        ----------
            torques: list
        """

        return [self.wheel_1_torque, self.wheel_1_torque]

    def get_wheels_radius(self):
        """
        Get the radii of the wheels

        Return
        ----------
            radius: list
        """

        return [self.wheel_1_radius, self.wheel_2_radius]

    def spring_length(self, node_i, node_j):
        """
        Get the spring length between node i and j.

        Return
        ----------
            spring length : float

        """

        nodes_coordinates = np.array(
            [
                [self.wheel_1_x, self.wheel_1_y],
                [self.wheel_2_x, self.wheel_2_y],
                [self.body_1_x, self.body_1_y],
                [self.body_2_x, self.body_2_y],
            ]
        )

        x_1 = nodes_coordinates[node_i][0]
        y_1 = nodes_coordinates[node_i][1]

        x_2 = nodes_coordinates[node_j][0]
        y_2 = nodes_coordinates[node_j][1]

        delta_x = x_1 - x_2
        delta_y = y_1 - y_2

        my_spring_length = (delta_x**2 + delta_y**2) ** 0.5

        return my_spring_length

    def get_springs_length(self):
        """
        Get all springs' lengths.

        Return
        ----------
            spring length : array, shape = (4, 4)

        """

        springs_length = np.zeros((4, 4))
        for i in range(4):
            for j in range(4):

                if i == j:
                    springs_length[i][j] = 0
                else:
                    springs_length[i][j] = self.spring_length(i, j)

        return springs_length

    def get_masses(self):
        """
        Get all springs' masses.

        Return
        ----------
            spring mass : list

        """

        return [
            self.wheel_1_mass,
            self.wheel_2_mass,
            self.body_1_mass,
            self.body_2_mass,
        ]
