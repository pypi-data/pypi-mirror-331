"""
env.py
======

This module contains the `env` class, which simulates bike dynamics in a given environment.
It provides methods to set up the environment, run simulations, and evaluate the performance of bikes.

Classes
env
"""

import numpy as np
from tqdm import tqdm


class env:
    """
    Environment class for simulating bike dynamics.

    Parameters
    ----------
    g : float, optional
        Gravitational acceleration (default is -9.8).
    elasticiity : float, optional
        Elasticity coefficient (default is 0).
    x_max : int, optional
        Maximum x-coordinate (default is 1000).
    t_step : float, optional
        Time step for simulation (default is 0.01).
    starting_hight : float, optional
        Starting height of the bike (default is 10).
    delta_x : float, optional
        Delta x for ground discretization (default is 0.001).
    ground : np.ndarray, optional
        Ground profile (default is a flat ground).
    ground_derivative : np.ndarray, optional
        Derivative of the ground profile (default is a flat ground).

    Attributes
    ----------
    elasticiity : float
        Elasticity coefficient.
    trajectory : list
        List to store the trajectory of bikes.
    n_bikes : int
        Number of bikes in the environment.
    t : float
        Current time in the simulation.
    t_step : float
        Time step for simulation.
    bikes : list
        List of bikes in the environment.
    starting_positions : np.ndarray
        Starting positions of the bikes.
    x_max : int
        Maximum x-coordinate.
    delta_x : float
        Delta x for ground discretization.
    ground_derivative : np.ndarray
        Derivative of the ground profile.
    ground : np.ndarray
        Ground profile.
    Ms : np.ndarray
        Mass matrix for the bikes.
    g : float
        Gravitational acceleration.
    K : np.ndarray
        Spring constant matrix.
    R : np.ndarray
        Position matrix.
    B : np.ndarray
        Damping coefficient matrix.
    Torks : np.ndarray
        Torque matrix.
    Init_lengths : np.ndarray
        Initial lengths of the springs.
    Radiuses : np.ndarray
        Radii of the bike wheels.

    Methods
    -------
    get_R()
        Returns the position matrix R.
    get_K()
        Returns the spring constant matrix K.
    get_B()
        Returns the damping coefficient matrix B.
    get_Ms()
        Returns the mass matrix Ms.
    get_torks()
        Returns the torque matrix.
    get_init_lenghs()
        Returns the initial lengths of the springs.
    get_Radius()
        Returns the radii of the bike wheels.
    set_bikes(list_bikes)
        Sets the list of bikes in the environment.
    get_trajectory_sizes()
        Returns the trajectory and radii of the bikes.
    evaluate()
        Evaluates the performance of the bikes.
    run(n)
        Runs the simulation for n steps.
    step()
        Performs a single simulation step using the Runge-Kutta method.
    apply_touching_effect(K, n_hat, is_touched)
        Applies the effect of touching the ground to the velocity matrix.
    calculate_acceleration(V, R, t)
        Calculates the acceleration of the bikes.
    cal_gravity_force()
        Calculates the gravitational force on the bikes.
    get_distance_distance_unit_vector(R)
        Returns the distance and unit distance vectors between bike components.
    cal_spring_force(R)
        Calculates the spring force on the bikes.
    cal_damping_force(V)
        Calculates the damping force on the bikes.
    perpendicular_unit_vector(touch_point_x)
        Returns the perpendicular unit vector at the touch points.
    parallel_unit_vector(touch_point_x)
        Returns the parallel unit vector at the touch points.
    get_connection_info(pos)
        Returns the connection information of the bikes with the ground.
    calculate_forces(R, V, t)
        Calculates the forces acting on the bikes.
    """

    def __init__(
        self,
        g=-9.8,
        elasticiity=0,
        x_max=1000,
        t_step=0.01,
        starting_hight=10,
        delta_x=0.001,
        ground=np.array(
            [
                np.linspace(0, 1000, int(1000 / 0.001)),
                0 * np.linspace(0, 1000, int(1000 / 0.001)),
            ]
        ).T,
        ground_derivative=np.array(
            [
                np.linspace(0, 1000, int(1000 / 0.001)),
                0 * np.linspace(0, 1000, int(1000 / 0.001)),
            ]
        ).T,
    ):
        """
        Initialize the environment for the genetic bike simulation.
        Parameters
        ----------
        g : float, optional
            Gravitational acceleration (default is -9.8).
        elasticiity : float, optional
            Elasticity coefficient (default is 0).
        x_max : int, optional
            Maximum x-coordinate value (default is 1000).
        t_step : float, optional
            Time step in seconds (default is 0.01).
        starting_hight : float, optional
            Starting height of the bike (default is 10).
        delta_x : float, optional
            Increment in x-coordinate (default is 0.001).
        ground : np.ndarray, optional
            Ground profile as a 2D array (default is a flat ground).
        ground_derivative : np.ndarray, optional
            Derivative of the ground profile as a 2D array (default is a flat ground derivative).
        Attributes
        ----------
        elasticiity : float
            Elasticity coefficient.
        trajectory : list
            List to store the trajectory of the bikes.
        n_bikes : int
            Number of bikes in the simulation.
        t : float
            Current time in the simulation.
        t_step : float
            Time step in seconds.
        bikes : list
            List to store the bike objects.
        starting_positions : np.ndarray
            Starting positions of the bikes.
        x_max : int
            Maximum x-coordinate value.
        delta_x : float
            Increment in x-coordinate.
        ground_derivative : np.ndarray
            Derivative of the ground profile.
        ground : np.ndarray
            Ground profile.
        Ms : np.ndarray
            Array to store the state of the bikes.
        g : float
            Gravitational acceleration.
        K : None
            Placeholder for spring constant.
        R : None
            Placeholder for damping coefficient.
        B : None
            Placeholder for another parameter.
        Torks : None
            Placeholder for torques.
        Init_lengths : None
            Placeholder for initial lengths.
        Radiuses : None
            Placeholder for radii.
        """

        self.elasticiity = elasticiity
        self.trajectory = []
        self.n_bikes = 0
        self.t = 0
        self.t_step = t_step  # t step in seconds
        self.bikes = []
        self.starting_positions = np.array([0, starting_hight])
        self.x_max = x_max
        self.delta_x = delta_x
        self.ground_derivative = ground_derivative
        self.ground = ground
        self.Ms = np.zeros((self.n_bikes, 4))
        self.g = g
        self.K = None
        self.R = None
        self.B = None
        self.Ms = None
        self.Torks = None
        self.Init_lengths = None
        self.Radiuses = None
        self.trajectory = None

    def get_R(self):
        """
        Get the coordinates matrix R for all bikes.
        This method generates a matrix R of shape (n_bikes, 4, 2) where each entry
        contains the coordinates of the bikes adjusted by their starting positions.
        Returns
        -------
        numpy.ndarray
            A 3D numpy array of shape (n_bikes, 4, 2) containing the coordinates
            of the bikes.
        """

        R = np.zeros((self.n_bikes, 4, 2))
        for i in range(len(self.bikes)):
            R[i, :, :] = self.bikes[i].get_coordinates() + self.starting_positions
        return R

    def get_K(self):
        """
        Compute the stiffness matrix K for all bikes.
        The stiffness matrix K is a 3-dimensional numpy array where each 2D slice
        corresponds to the stiffness matrix of a single bike. The stiffness matrix
        for each bike is computed by subtracting the diagonal matrix of the sum of
        spring constants from the matrix of spring constants.
        Returns
        -------
        numpy.ndarray
            A 3-dimensional array of shape (n_bikes, 4, 4) containing the stiffness
            matrices for all bikes.
        """

        K = np.zeros((self.n_bikes, 4, 4))
        for i in range(len(self.bikes)):
            ks = self.bikes[i].get_springs_k()
            K[i, :, :] = ks - np.diag(np.sum(ks, axis=0))

        return K

    def get_B(self):
        """
        Compute the B matrix for the bikes.
        The B matrix is a 3-dimensional numpy array where each 2D slice corresponds to a bike.
        Each 2D slice is computed by subtracting the diagonal matrix of the sum of spring losses
        from the spring losses matrix of the bike.
        Returns
        -------
        numpy.ndarray
            A 3-dimensional array of shape (n_bikes, 4, 4) representing the B matrices for all bikes.
        """

        B = np.zeros((self.n_bikes, 4, 4))
        for i in range(len(self.bikes)):
            bs = self.bikes[i].get_springs_loss()
            B[i, :, :] = bs - np.diag(np.sum(bs, axis=0))
        return B

    def get_Ms(self):
        """
        Retrieve the masses of all bikes.

        This function creates a numpy array where each row corresponds to the masses
        of a bike. The masses are retrieved from the `get_masses` method of each bike
        object.

        Returns
        -------
        numpy.ndarray
            A 2D array of shape (n_bikes, 4) where each row contains the masses of a bike.
        """
        ms = np.zeros((self.n_bikes, 4))
        for i in range(len(self.bikes)):
            ms[i] = self.bikes[i].get_masses()
        return ms

    def get_torks(self):
        """
        Get the torques for all bikes.
        This function initializes a numpy array to store the torques for each bike.
        It then iterates over the list of bikes and retrieves the torques for each bike,
        storing them in the corresponding row of the array.
        Returns
        -------
        numpy.ndarray
            A 2D array of shape (n_bikes, 2) containing the torques for each bike.
        """

        torks = np.zeros((self.n_bikes, 2))
        for i in range(len(self.bikes)):
            torks[i, :] = self.bikes[i].get_torques()
        return torks

    def get_init_lenghs(self):
        """
        Get the initial lengths of the springs for all bikes.
        This method initializes a numpy array with zeros and then fills it with the
        spring lengths for each bike in the `self.bikes` list.
        Returns
        -------
        numpy.ndarray
            A 3D numpy array of shape (n_bikes, 4, 4) containing the spring lengths
            for each bike.
        """
        lengths = np.zeros((self.n_bikes, 4, 4))
        for i in range(len(self.bikes)):
            lengths[i, :, :] = self.bikes[i].get_springs_length()

        return lengths

    def get_Radius(self):
        """
        Get the radius of the wheels for all bikes.
        This function retrieves the radius of the wheels for each bike in the environment.
        It returns a numpy array where each row corresponds to a bike and contains the radii
        of its wheels.
        Returns
        -------
        numpy.ndarray
            A 2D array of shape (n_bikes, 2) where each row contains the radius of the wheels
            for a bike.
        """

        radisuss = np.zeros((self.n_bikes, 2))
        for i in range(self.n_bikes):
            radisuss[i] = self.bikes[i].get_wheels_radius()

        return radisuss

    def set_bikes(self, list_bikes):
        """
        Set the list of bikes and initialize related parameters.
        Parameters
        ----------
        list_bikes : list
            A list containing bike objects to be set.
        Attributes
        ----------
        bikes : list
            The list of bike objects.
        n_bikes : int
            The number of bikes in the list.
        B : type
            The result of the get_B() method.
        K : type
            The result of the get_K() method.
        Ms : type
            The result of the get_Ms() method.
        Init_lengths : type
            The result of the get_init_lengths() method.
        Torks : type
            The result of the get_torks() method.
        R : type
            The result of the get_R() method.
        R0 : type
            The result of the get_R() method.
        Radiuses : type
            The result of the get_Radius() method.
        """
        self.bikes = list_bikes
        self.n_bikes = len(list_bikes)
        self.B = self.get_B()
        self.K = self.get_K()
        self.Ms = self.get_Ms()
        self.Init_lengths = self.get_init_lenghs()
        self.Torks = self.get_torks()
        self.R = self.get_R()
        self.R0 = self.get_R()
        self.Radiuses = self.get_Radius()

    def get_trajectory_sizes(self):
        """
        Get the trajectory and radius sizes.
        Returns
        -------
        tuple
            A tuple containing the trajectory and radius sizes.
        """

        return self.trajectory, self.Radiuses

    def evaluate(self):
        """
        Evaluate the mass center change of the system and determine if any part of the system has failed.
        The function calculates the change in the mass center of the system based on the difference between
        the current positions and the initial positions. It also checks if any part of the system has failed
        by comparing the y-coordinates of the trajectory with the ground level.
        Returns
        -------
        mass_center_change : ndarray
            An array representing the change in the mass center of the system. If any part of the system has
            failed, the corresponding mass center change is set to 0.
        """

        delta_X = self.R[:, :, 0] - self.R0[:, :, 0]
        ys = self.trajectory[:, :, 2:, 1]
        y_ground = self.ground[
            (self.trajectory[:, :, 2:, 0] / self.delta_x).astype(np.int64), 1
        ]
        mass_center_change = np.sum(delta_X * self.Ms, axis=1) / np.sum(self.Ms, axis=1)
        lower = ys < y_ground
        failed = np.any(lower, axis=(0, 2))
        # where_failed = np.argwhere(lower)
        # wheels_x = self.trajectory[:, :, 2:, 0]
        # print(where_failed, where_failed.shape, wheels_x.shape)
        # wheels_x[where_failed[:, 0], where_failed[:, 1], where_failed[:, 2]].shape

        mass_center_change[failed] = 0

        return mass_center_change

    def run(self, n):
        """
        Simulate the environment for a given number of steps.
        Parameters
        ----------
        n : int
            The number of steps to simulate.
        Returns
        -------
        trajectory : numpy.ndarray
            A 4-dimensional array of shape (n, self.n_bikes, 4, 2) representing the trajectory of the bikes.
        scores : numpy.ndarray
            An array containing the evaluation scores after the simulation.
        """

        self.trajectory = np.zeros((n, self.n_bikes, 4, 2))
        self.t = 0
        self.V = np.zeros((self.n_bikes, 4, 2))

        for i in tqdm(range(n)):
            self.step()
            self.trajectory[i, :, :] = self.R

        self.scores = self.evaluate()

        return self.trajectory, self.scores

    def step(self):
        """
        Perform one step of the simulation using the Runge-Kutta method.
        This method updates the state variables `V` (velocity), `R` (position), and `t` (time)
        by solving the differential equations using the 4th-order Runge-Kutta method. It also
        applies any necessary effects if the object is touching another object.
        Returns
        -------
        None
        """
        a1, n_hat, is_touched = self.calculate_acceleration(self.V, self.R, self.t)
        k1 = self.t_step * a1
        k1 = self.apply_touching_effect(k1, n_hat, is_touched)
        theta1 = self.V

        a2, n_hat, is_touched = self.calculate_acceleration(
            self.V + k1 / 2, self.R + theta1 / 2, self.t + self.t_step / 2
        )
        k2 = self.t_step * a2
        k2 = self.apply_touching_effect(k2, n_hat, is_touched)
        theta2 = self.V + k1 / 2

        a3, n_hat, is_touched = self.calculate_acceleration(
            self.V + k2 / 2, self.R + theta2 / 2, self.t + self.t_step / 2
        )
        k3 = self.t_step * a3
        k3 = self.apply_touching_effect(k3, n_hat, is_touched)
        theta3 = self.V + k2 / 2

        a4, n_hat, is_touched = self.calculate_acceleration(
            self.V + k3, self.R + theta3, self.t + self.t_step
        )
        k4 = self.t_step * a4
        k4 = self.apply_touching_effect(k4, n_hat, is_touched)
        theta4 = self.V + k3

        self.V = self.V + (k1 + 2 * k2 + 2 * k3 + k4) / 6
        self.V = self.apply_touching_effect(self.V, n_hat, is_touched)
        self.R = self.R + (theta1 + 2 * theta2 + 2 * theta3 + theta4) / 6
        self.t += self.t_step

    def apply_touching_effect(self, K, n_hat, is_touched):
        """
        Apply the touching effect to the velocity matrix K based on the normal vector and touching status.
        Parameters
        ----------
        K : numpy.ndarray
            The velocity matrix of shape (n_bikes, 3, 3).
        n_hat : numpy.ndarray
            The normal vector of shape (n_bikes, 2, 1).
        is_touched : numpy.ndarray
            A boolean array of shape (n_bikes, 2) indicating whether each bike is touched.
        Returns
        -------
        numpy.ndarray
            The updated velocity matrix K after applying the touching effect.
        """
        dv_n = n_hat * is_touched.reshape((self.n_bikes, 2, 1)) * (1 + self.elasticiity)

        V_dot_n_hat = np.sum(K[:, :2, :] * n_hat, axis=2).reshape((self.n_bikes, 2, 1))

        K[:, :2, :] -= V_dot_n_hat * dv_n

        return K

    def calculate_acceleration(self, V, R, t):
        """
        Calculate the acceleration of the bikes.
        Parameters
        ----------
        V : ndarray
            The velocity of the bikes, shape (n_bikes, 4).
        R : ndarray
            The position of the bikes, shape (n_bikes, 4).
        t : float
            The current time.
        Returns
        -------
        tuple
            A tuple containing:
            - acceleration : ndarray
                The calculated acceleration of the bikes, shape (n_bikes, 4, 2).
            - n_hat : ndarray
                The normal vector, shape (n_bikes, 4).
            - is_touched : ndarray
                Boolean array indicating if the bikes' wheels are in contact with the ground, shape (n_bikes, 4).
        """

        force, n_hat, is_touched = self.calculate_forces(R, V, t)
        return (
            force / np.repeat(self.Ms.reshape((self.n_bikes, 4, 1)), 2, axis=2),
            n_hat,
            is_touched,
        )

    def cal_gravity_force(self):
        """
        Calculate the gravity force acting on the bikes.
        This method calculates the gravity force for each bike and returns it as a numpy array.
        The gravity force is calculated based on the mass of the bikes and the gravitational acceleration.
        Returns
        -------
        numpy.ndarray
            A numpy array of shape (n_bikes, 4, 2) where the gravity force is stored in the second column.
        """

        W = np.zeros((self.n_bikes, 4, 2))
        W[:, :, 1] = self.Ms * self.g
        return W

    def get_distance_distance_unit_vector(self, R):
        """
        Calculate the distance and normalized distance unit vectors between masses in bikes.
        Parameters
        ----------
        R : numpy.ndarray
            A numpy array of shape (n_bikes * 4 * 2) representing the positions of the masses in bikes.
        Returns
        -------
        distance : numpy.ndarray
            A numpy array of shape (n_bikes, 4, 4, 2) representing the distance vectors between masses in bikes.
        normalized_distances : numpy.ndarray
            A numpy array of shape (n_bikes, 4, 4, 2) representing the normalized distance unit vectors between masses in bikes.
        """

        R = R.reshape(self.n_bikes, 4, 1, 2)
        tiled = np.tile(R, (1, 1, 4, 1))

        transposed = tiled.transpose((0, 2, 1, 3))

        distance = transposed - tiled

        normalized_distances = distance / np.linalg.norm(distance, axis=3).reshape(
            -1, 4, 4, 1
        )
        normalized_distances[:, range(4), range(4)] = 0

        return distance, normalized_distances

    def cal_spring_force(self, R):
        """
        Calculate the spring force based on the given position vector R.
        Parameters
        ----------
        R : ndarray
            The position vector of shape (n, 4, 4, 3) where n is the number of particles.
        Returns
        -------
        spring_force : ndarray
            The calculated spring force of shape (n, 4, 4, 3).
        """

        d, d_hat = self.get_distance_distance_unit_vector(R)

        x = d - (d_hat * self.Init_lengths.reshape(-1, 4, 4, 1))

        spring_force = np.sum(-self.K.reshape(-1, 4, 4, 1) * x, axis=1)

        return spring_force

    def cal_damping_force(self, V):
        """
        Calculate the damping force.
        Parameters
        ----------
        V : numpy.ndarray
            The velocity vector.
        Returns
        -------
        numpy.ndarray
            The damping force vector.
        """

        return self.B @ V

    def perpendicular_unit_vector(self, touch_point_x):
        """
        Calculate the perpendicular unit vector at a given touch point.
        Parameters
        ----------
        touch_point_x : int
            The x-coordinate index of the touch point on the ground.
        Returns
        -------
        n_hat : numpy.ndarray
            A numpy array of shape (n_bikes, 2, 2) representing the perpendicular unit vectors.
            The first dimension corresponds to the number of bikes, the second dimension
            corresponds to the two components of the vector, and the third dimension
            corresponds to the x and y components of the unit vector.
        """

        n_hat = np.zeros((self.n_bikes, 2, 2))

        f_primes = self.ground_derivative[touch_point_x][:, :, 1]

        n_hat[:, :, 0] = -f_primes / (1 + f_primes**2) ** 0.5
        n_hat[:, :, 1] = 1 / (1 + f_primes**2) ** 0.5

        return n_hat

    def parallel_unit_vector(self, touch_point_x):
        """
        Calculate the parallel unit vector at a given touch point.
        Parameters
        ----------
        touch_point_x : int
            The x-coordinate of the touch point on the ground.
        Returns
        -------
        t_hat : numpy.ndarray
            A 3D array of shape (n_bikes, 2, 2) representing the parallel unit vectors.
            The first dimension corresponds to the number of bikes, the second dimension
            corresponds to the vector components, and the third dimension corresponds to
            the x and y components of the unit vector.
        """

        t_hat = np.zeros((self.n_bikes, 2, 2))

        f_primes = self.ground_derivative[touch_point_x][:, :, 1]

        t_hat[:, :, 0] = 1 / (1 + f_primes**2) ** 0.5
        t_hat[:, :, 1] = f_primes / (1 + f_primes**2) ** 0.5

        return t_hat

    def get_connection_info(self, pos):
        """
        Calculate the minimum distance from each bike to the ground, the closest point on the ground,
        and whether each bike's wheel is touching the ground.
        Parameters
        ----------
        pos : ndarray
            A numpy array of shape (n_bikes, 2) representing the positions of the bikes.
        Returns
        -------
        min_distacne : ndarray
            A numpy array of shape (n_bikes,) representing the minimum distance from each bike to the ground.
        closest_point_x : ndarray
            A numpy array of shape (n_bikes,) representing the x-coordinate of the closest point on the ground for each bike.
        is_touched : ndarray
            A boolean numpy array of shape (n_bikes,) indicating whether each bike's wheel is touching the ground.
        """

        tiled_ground = np.tile(self.ground, (self.n_bikes, 2, 1, 1)).transpose(
            (2, 0, 1, 3)
        )

        norm_distacnes_from_ground = np.linalg.norm(tiled_ground - pos, axis=3)

        min_distacne = np.min(norm_distacnes_from_ground, axis=0)

        closest_point_x = np.argmin(norm_distacnes_from_ground, axis=0)

        is_touched = min_distacne - self.Radiuses < 1e-5

        return min_distacne, closest_point_x, is_touched

    def calculate_forces(self, R, V, t):
        """
        Calculate the forces acting on the bikes.
        Parameters
        ----------
        R : ndarray
            An array of shape (n_bikes, 4, 2) representing the positions of the bikes.
        V : ndarray
            An array of shape (n_bikes, 4, 2) representing the velocities of the bikes.
        t : float
            The current time.
        Returns
        -------
        force : ndarray
            An array of shape (n_bikes, 4, 2) representing the calculated forces on the bikes.
        n_hat : ndarray
            An array representing the perpendicular unit vectors at the closest points of contact.
        is_touched : ndarray
            An array indicating whether each bike is in contact with another object.
        """

        force = np.zeros((self.n_bikes, 4, 2))

        W = self.cal_gravity_force()
        spring_force = self.cal_spring_force(R)
        damping_force = self.cal_damping_force(V)

        min_distacne, closest_point_x, is_touched = self.get_connection_info(
            R[:, :2, :]
        )

        n_hat = self.perpendicular_unit_vector(closest_point_x)
        t_hat = self.parallel_unit_vector(closest_point_x)

        turk_force = np.zeros((self.n_bikes, 4, 2))

        turk_force[:, :2, :] = t_hat * (self.Torks * is_touched).reshape(
            (self.n_bikes, 2, 1)
        )

        force += W + turk_force + spring_force + damping_force

        return force, n_hat, is_touched
