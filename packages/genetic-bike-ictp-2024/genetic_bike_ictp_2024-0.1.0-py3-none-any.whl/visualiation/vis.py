import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

"""
Visualization module for animating the trajectory of a bike simulation.

This module contains the `Vis` class which is responsible for creating an animation
of the bike's trajectory over a given number of steps.

Classes
-------
Vis
    A class used to visualize the trajectory of a bike simulation.

"""


class Vis:
    """
    A class used to visualize the trajectory of a system over time.
    Attributes
    ----------
    trajectory : numpy.ndarray
        A 3D array representing the trajectory of points in the system.
    radiuss : list of float
        A list containing the radii of the circles to be drawn.
    steps : int
        The number of steps in the animation.
    ground : numpy.ndarray
        A 2D array representing the ground line.
    Methods
    -------
    run()
        Initializes the figure and starts the animation.
    animate(i)
        Updates the plot for the i-th frame of the animation.
    """

    def __init__(self, trajectory, radiuss, steps, ground):
        """
        Initialize the visualization parameters.
        Parameters
        ----------
        trajectory : list
            A list representing the trajectory of the bike.
        radiuss : float
            The radius of the bike's wheels.
        steps : int
            The number of steps in the simulation.
        ground : object
            The ground object representing the surface on which the bike moves.
        """

        self.trajectory = trajectory
        self.radiuss = radiuss
        self.steps = steps
        self.ground = ground

    def run(self):
        """
        Initializes the figure and axes for the plot, and starts the animation.
        This method sets up a matplotlib figure and axes, then creates an animation
        using the `FuncAnimation` class. The animation updates the plot at each step
        and displays it in a zoomable GUI mode.
        Parameters
        ----------
        None
        Returns
        -------
        None
        """

        self.figure = plt.figure()
        self.axes = self.figure.add_subplot(111)
        # afterwards, switch to zoomable GUI mode

        ani = animation.FuncAnimation(
            self.figure, self.animate, np.arange(1, self.steps), interval=1
        )

        writer = animation.PillowWriter(
            fps=15, metadata=dict(artist="Me"), bitrate=1800
        )
        ani.save("animation.gif", writer=writer)

        plt.show()

    def animate(self, i):
        """
        Animate the trajectory of the bike at a given frame index.
        Parameters
        ----------
        i : int
            The frame index to animate.
        Returns
        -------
        tuple
            A tuple containing the matplotlib Circle patches for the animated balls.
        """

        plt.cla()
        plt.gca().set_aspect("equal")
        plt.xlabel("x [m]")
        plt.ylabel("h [m]")

        self.axes.set_xlim(-2, 20)
        self.axes.set_ylim(-5, 20)

        plt.plot(
            [self.trajectory[i, 0, 0], self.trajectory[i, 1, 0]],
            [self.trajectory[i, 0, 1], self.trajectory[i, 1, 1]],
            color="red",
        )

        plt.plot(
            [self.trajectory[i, 0, 0], self.trajectory[i, 2, 0]],
            [self.trajectory[i, 0, 1], self.trajectory[i, 2, 1]],
            color="red",
        )

        plt.plot(
            [self.trajectory[i, 0, 0], self.trajectory[i, 3, 0]],
            [self.trajectory[i, 0, 1], self.trajectory[i, 3, 1]],
            color="red",
        )

        plt.plot(
            [self.trajectory[i, 1, 0], self.trajectory[i, 2, 0]],
            [self.trajectory[i, 1, 1], self.trajectory[i, 2, 1]],
            color="red",
        )

        plt.plot(
            [self.trajectory[i, 1, 0], self.trajectory[i, 3, 0]],
            [self.trajectory[i, 1, 1], self.trajectory[i, 3, 1]],
            color="red",
        )

        plt.plot(
            [self.trajectory[i, 2, 0], self.trajectory[i, 3, 0]],
            [self.trajectory[i, 2, 1], self.trajectory[i, 3, 1]],
            color="red",
        )

        plt.plot(
            self.ground[:, 0], self.ground[:, 1], color="black", alpha=0.5, linewidth=10
        )

        ball1 = plt.Circle(
            self.trajectory[i, 0],
            radius=self.radiuss[0],
            edgecolor="blue",
            facecolor="white",
            linewidth=5,
        )
        ball2 = plt.Circle(
            self.trajectory[i, 1],
            radius=self.radiuss[1],
            edgecolor="blue",
            facecolor="white",
            linewidth=5,
        )
        ball3 = plt.Circle(self.trajectory[i, 2], radius=0.5, color="black")
        ball4 = plt.Circle(self.trajectory[i, 3], radius=0.5, color="black")

        self.axes.add_patch(ball1)
        self.axes.add_patch(ball2)
        self.axes.add_patch(ball3)
        self.axes.add_patch(ball4)

        return (
            ball1,
            ball2,
            ball3,
            ball4,
        )
