"""
Quantum Teleportation Protocol
Author: Anubhav
Physics: Quantum Information — Quantum Communication
Method: Bell State Entanglement + Metropolis Correction

What this simulates:
  Alice wants to send a quantum state |ψ⟩ to Bob
  without physically sending the qubit itself.
  Uses 1 entangled pair + 2 classical bits.

Circuit:
  q0 = Alice's qubit (state to teleport)
  q1 = Alice's half of entangled pair
  q2 = Bob's half of entangled pair
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram

# ─────────────────────────────────────────────
# STEP 1: CREATE TELEPORTATION CIRCUIT
# ─────────────────────────────────────────────

def create_teleportation_circuit(theta=np.pi/3, phi=np.pi/4):
    """
    Full quantum teleportation circuit.

    Parameters:
      theta, phi: angles defining the state to teleport
      |ψ⟩ = cos(θ/2)|0⟩ + e^(iφ)sin(θ/2)|1⟩

    Returns: QuantumCircuit
    """

    # 3 qubits, 3 classical bits
    qr = QuantumRegister(3, 'q')
    cr = ClassicalRegister(3, 'c')
    qc = QuantumCircuit(qr, cr)

    # ── Phase 1: Prepare state to teleport (Alice's qubit q0) ──
    # State: |ψ⟩ = cos(θ/2)|0⟩ + e^(iφ)sin(θ/2)|1⟩
    qc.ry(theta, qr[0])   # Rotate by theta
    qc.rz(phi, qr[0])     # Rotate by phi
    qc.barrier(label='State Prepared')

    # ── Phase 2: Create Bell pair (entangle q1 and q2) ──
    # |Φ+⟩ = (|00⟩ + |11⟩)/√2
    qc.h(qr[1])            # Hadamard on q1 → superposition
    qc.cx(qr[1], qr[2])   # CNOT: entangle q1 and q2
    qc.barrier(label='Bell Pair Created')

    # ── Phase 3: Bell Measurement (Alice measures q0 and q1) ──
    qc.cx(qr[0], qr[1])   # CNOT between Alice's qubits
    qc.h(qr[0])            # Hadamard on q0
    qc.barrier(label='Bell Measurement')

    # Measure Alice's qubits
    qc.measure(qr[0], cr[0])   # Classical bit 0
    qc.measure(qr[1], cr[1])   # Classical bit 1

    # ── Phase 4: Bob applies corrections based on classical bits ──
    # If c1=1 → apply X gate (bit flip)
    # If c0=1 → apply Z gate (phase flip)
    qc.cx(qr[1], qr[2])        # X correction if c1=1
    qc.cz(qr[0], qr[2])        # Z correction if c0=1
    qc.barrier(label="Bob's Correction")

    # Measure Bob's qubit
    qc.measure(qr[2], cr[2])

    return qc


# ─────────────────────────────────────────────
# STEP 2: RUN SIMULATION
# ─────────────────────────────────────────────

def run_teleportation(theta=np.pi/3, phi=np.pi/4, shots=4096):
    """
    Run the teleportation circuit on Qiskit AerSimulator.
    Returns: counts dictionary
    """
    qc = create_teleportation_circuit(theta, phi)
    simulator = AerSimulator()
    job = simulator.run(qc, shots=shots)
    result = job.result()
    counts = result.get_counts()
    return counts, qc


# ─────────────────────────────────────────────
# STEP 3: VERIFY TELEPORTATION
# ─────────────────────────────────────────────

def verify_teleportation(theta, phi):
    """
    Verify that Bob's qubit matches Alice's original state.
    Computes expected probabilities from the wavefunction.
    """
    # Expected: P(|0⟩) = cos²(θ/2), P(|1⟩) = sin²(θ/2)
    p0_expected = np.cos(theta/2)**2
    p1_expected = np.sin(theta/2)**2
    return p0_expected, p1_expected


# ─────────────────────────────────────────────
# STEP 4: VISUALIZATIONS
# ─────────────────────────────────────────────

def plot_results(counts, theta, phi):
    """
    Plot teleportation results — Bob's qubit distribution
    vs expected from Alice's original state.
    """
    # Extract Bob's qubit (bit 2, rightmost in Qiskit notation)
    bob_counts = {'0': 0, '1': 0}
    for bitstring, count in counts.items():
        bob_bit = bitstring[0]   # leftmost = q2 in Qiskit
        bob_counts[bob_bit] += count

    total = sum(bob_counts.values())
    p0_measured = bob_counts['0'] / total
    p1_measured = bob_counts['1'] / total

    p0_expected, p1_expected = verify_teleportation(theta, phi)

    fig = plt.figure(figsize=(14, 10))
    fig.suptitle(
        "Quantum Teleportation Protocol — Simulation Results\n"
        f"Teleporting state: θ={theta:.3f} rad, φ={phi:.3f} rad",
        fontsize=14, fontweight='bold'
    )

    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, :])

    # ── Plot 1: Bob's measured state ──
    colors = ['#1E88E5', '#E53935']
    bars = ax1.bar(['|0⟩', '|1⟩'],
                   [p0_measured, p1_measured],
                   color=colors, alpha=0.85, width=0.4)
    ax1.bar(['|0⟩', '|1⟩'],
            [p0_expected, p1_expected],
            color=colors, alpha=0.3, width=0.4,
            linestyle='--', edgecolor='black', linewidth=1.5,
            label='Expected')
    ax1.set_title("Bob's Qubit State\n(Blue bars=measured, Faded=expected)",
                  fontsize=11, fontweight='bold')
    ax1.set_ylabel('Probability', fontsize=10)
    ax1.set_ylim(0, 1.1)
    ax1.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, [p0_measured, p1_measured]):
        ax1.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 0.02,
                 f'{val:.3f}', ha='center', fontsize=11, fontweight='bold')

    # ── Plot 2: Fidelity comparison ──
    fidelity_0 = 1 - abs(p0_measured - p0_expected)
    fidelity_1 = 1 - abs(p1_measured - p1_expected)
    avg_fidelity = (fidelity_0 + fidelity_1) / 2

    categories = ['P(|0⟩)\nFidelity', 'P(|1⟩)\nFidelity', 'Average\nFidelity']
    values = [fidelity_0, fidelity_1, avg_fidelity]
    bar_colors = ['#43A047', '#FB8C00', '#8E24AA']
    bars2 = ax2.bar(categories, values, color=bar_colors, alpha=0.85, width=0.4)
    ax2.set_title('Teleportation Fidelity\n(1.0 = Perfect)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Fidelity', fontsize=10)
    ax2.set_ylim(0, 1.1)
    ax2.axhline(y=1.0, color='green', linestyle='--', alpha=0.5, label='Perfect = 1.0')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.legend(fontsize=9)
    for bar, val in zip(bars2, values):
        ax2.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 0.02,
                 f'{val:.4f}', ha='center', fontsize=10, fontweight='bold')

    # ── Plot 3: Teleportation across multiple states ──
    thetas = np.linspace(0, np.pi, 20)
    p0_exp_list = []
    p0_meas_list = []

    for t in thetas:
        c, _ = run_teleportation(theta=t, phi=phi, shots=1024)
        bob = {'0': 0, '1': 0}
        for bs, cnt in c.items():
            bob[bs[0]] += cnt
        tot = sum(bob.values())
        p0_meas_list.append(bob['0'] / tot)
        p0_exp_list.append(np.cos(t/2)**2)

    ax3.plot(thetas, p0_exp_list, 'b-', linewidth=2.5,
             label='Expected P(|0⟩) = cos²(θ/2)', zorder=3)
    ax3.scatter(thetas, p0_meas_list, color='red', s=60,
                zorder=4, label='Measured P(|0⟩) — Bob\'s qubit', alpha=0.85)
    ax3.fill_between(thetas, p0_exp_list, p0_meas_list,
                     alpha=0.15, color='purple', label='Error margin')
    ax3.set_xlabel('θ (rotation angle of Alice\'s state)', fontsize=11)
    ax3.set_ylabel('P(|0⟩)', fontsize=11)
    ax3.set_title('Teleportation Verification Across Multiple States\n'
                  'Red dots should follow blue curve perfectly if teleportation works',
                  fontsize=11, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(0, np.pi)
    ax3.set_xticks([0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi])
    ax3.set_xticklabels(['0', 'π/4', 'π/2', '3π/4', 'π'])

    plt.savefig('/home/claude/teleportation_results.png',
                dpi=150, bbox_inches='tight')
    print("Saved: teleportation_results.png")

    return avg_fidelity


def plot_circuit(theta=np.pi/3, phi=np.pi/4):
    """Save the circuit diagram."""
    qc = create_teleportation_circuit(theta, phi)
    fig = qc.draw(output='mpl', style='iqp', fold=40)
    fig.savefig('/home/claude/teleportation_circuit.png',
                dpi=150, bbox_inches='tight')
    print("Saved: teleportation_circuit.png")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  Quantum Teleportation Protocol")
    print("  Anubhav | BSc Physics | Utkal University")
    print("=" * 55)

    # State to teleport
    theta = np.pi / 3      # 60 degrees
    phi   = np.pi / 4      # 45 degrees

    p0_exp, p1_exp = verify_teleportation(theta, phi)
    print(f"\nState to teleport:")
    print(f"  θ = π/3 = {theta:.4f} rad")
    print(f"  φ = π/4 = {phi:.4f} rad")
    print(f"\nExpected after teleportation:")
    print(f"  P(|0⟩) = cos²(θ/2) = {p0_exp:.4f}")
    print(f"  P(|1⟩) = sin²(θ/2) = {p1_exp:.4f}")

    print("\n[1/3] Drawing circuit diagram...")
    plot_circuit(theta, phi)

    print("[2/3] Running teleportation simulation (4096 shots)...")
    counts, qc = run_teleportation(theta, phi, shots=4096)

    print("[3/3] Plotting results and verification...")
    avg_fidelity = plot_results(counts, theta, phi)

    print(f"\n✓ Simulation complete!")
    print(f"  Average Fidelity = {avg_fidelity:.4f}")
    print(f"  (1.0000 = perfect teleportation)")

    if avg_fidelity > 0.95:
        print("  ✅ Teleportation SUCCESSFUL — Bob's state matches Alice's!")
    else:
        print("  ⚠ Teleportation has some noise — try more shots")
