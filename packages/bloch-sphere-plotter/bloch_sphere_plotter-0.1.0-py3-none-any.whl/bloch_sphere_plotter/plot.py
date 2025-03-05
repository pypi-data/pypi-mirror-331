import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_bloch_sphere(state):
    """
    Plots a single-qubit state on the Bloch sphere.

    Parameters:
    state (tuple): A tuple (theta, phi) representing the qubit state.

    Example:
    >>> plot_bloch_sphere((np.pi/3, np.pi/4))
    """
    theta, phi = state

    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Draw Bloch sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 50)
    X = np.outer(np.cos(u), np.sin(v))
    Y = np.outer(np.sin(u), np.sin(v))
    Z = np.outer(np.ones(np.size(u)), np.cos(v))

    # Improved sphere appearance
    ax.plot_surface(X, Y, Z, color='skyblue', alpha=0.2, edgecolor='lightgray', 
                    linewidth=0.5, rstride=5, cstride=5)
    
    # Add coordinate axes
    axes_length = 1.3
    ax.quiver(0, 0, 0, axes_length, 0, 0, color='k', arrow_length_ratio=0.1, linewidth=2)
    ax.quiver(0, 0, 0, 0, axes_length, 0, color='k', arrow_length_ratio=0.1, linewidth=2)
    ax.quiver(0, 0, 0, 0, 0, axes_length, color='k', arrow_length_ratio=0.1, linewidth=2)
    
    # Add axis labels at the end of arrows
    ax.text(axes_length+0.1, 0, 0, r'$|0\rangle$', fontsize=14)
    ax.text(0, axes_length+0.1, 0, r'$Y$', fontsize=14)
    ax.text(0, 0, axes_length+0.1, r'$|1\rangle$', fontsize=14)
    
    # Plot the qubit state vector with better arrow
    ax.quiver(0, 0, 0, x, y, z, color="red", arrow_length_ratio=0.15, linewidth=3)
    
    # Add a point at the end of the state vector
    ax.scatter([x], [y], [z], color='red', s=50)
    
    # Add equator circle
    equator_u = np.linspace(0, 2 * np.pi, 100)
    ax.plot(np.cos(equator_u), np.sin(equator_u), np.zeros_like(equator_u), 
            color='gray', linestyle='--', alpha=0.7)
    
    # Add meridian circles
    for angle in [0, np.pi/2, np.pi, 3*np.pi/2]:
        meridian_v = np.linspace(0, np.pi, 50)
        x_m = np.cos(angle) * np.sin(meridian_v)
        y_m = np.sin(angle) * np.sin(meridian_v)
        z_m = np.cos(meridian_v)
        ax.plot(x_m, y_m, z_m, color='gray', linestyle='--', alpha=0.7)
    
    # Remove axis panes and grid
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('w')
    ax.yaxis.pane.set_edgecolor('w')
    ax.zaxis.pane.set_edgecolor('w')
    ax.grid(False)
    
    # Set equal aspect ratio
    ax.set_box_aspect([1,1,1])
    
    # Remove numerical tick labels
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_zticklabels([])
    
    # Labels
    ax.set_xlabel("X", fontsize=14)
    ax.set_ylabel("Y", fontsize=14)
    ax.set_zlabel("Z", fontsize=14)
    ax.set_title("Bloch Sphere Representation", fontsize=16)
    
    # Add state information as text
    state_text = f"State: (θ={theta:.2f}, φ={phi:.2f})"
    fig.text(0.5, 0.02, state_text, ha='center', fontsize=12)

    plt.tight_layout()
    plt.show()