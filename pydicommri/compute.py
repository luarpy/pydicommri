from pydicommri.water import compute_water
from pydicommri.fat import compute_fat
from pydicommri.fatfraction import compute_ff

def compute(compute_type, *args):
    # args es una tupla que contiene el resto de los argumentos
    in_phase_path, opp_phase_path, output_mha_path = args
    if compute_type == "water":
        compute_water(in_phase_path, opp_phase_path, output_mha_path)
    elif compute_type == "fat":
        compute_fat(in_phase_path, opp_phase_path, output_mha_path)
    elif compute_type == 'fatfraction':
        compute_ff(in_phase_path, opp_phase_path, output_mha_path)
    else:
        print("Compute module not recognized",file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="PyDICOM MRI CLI")
    parser.add_argument('--compute', choices=['fat', 'water', 'fatfraction'], required=True, help="Selecciona el cálculo a realizar: fatfraction, 'fat' o 'water'")
    parser.add_argument("in_phase_path", help="Ruta del archivo de fase de entrada.")
    parser.add_argument("opp_phase_path", help="Ruta del archivo de fase de salida.")
    parser.add_argument("output_mha_path", help="Ruta del archivo MHA de salida.")

    args = parser.parse_args()

    # Llamar a la función compute pasando los argumentos en el orden correcto
    compute(args.compute, args.in_phase_path, args.opp_phase_path, args.output_mha_path)

if __name__ == "__main__":
    main()