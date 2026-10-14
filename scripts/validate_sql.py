import sys
from pathlib import Path

from pglast import parse_sql
from pglast.visitors import Visitor


class ValidarTipos(Visitor):
    def __init__(self):
        super().__init__()
        self.errores = []

    def visit_TypeName(self, ancestors, node):
        tipo = node.names[-1].sval.lower()

        if tipo in {"json", "jsonb"}:
            self.errores.append(f"Tipo prohibido: {tipo}")


def main():
    if len(sys.argv) != 2:
        print("Uso: python scripts/validate_sql.py RUTA")
        return 1

    ruta = Path(sys.argv[1])

    if ruta.is_file() and ruta.suffix.lower() == ".sql":
        archivos = [ruta]
    elif ruta.is_dir():
        archivos = sorted(ruta.rglob("*.sql"))
    else:
        print(f"ERROR: ruta SQL inexistente o no valida: {ruta}")
        return 1

    if not archivos:
        print("ERROR: no se encontraron archivos SQL.")
        return 1

    hay_errores = False

    for archivo in archivos:
        try:
            contenido = archivo.read_text(encoding="utf-8-sig")
            sentencias = parse_sql(contenido)
            validador = ValidarTipos()
            validador(sentencias)
        except Exception as error:
            print(f"ERROR: {archivo}: {error}")
            hay_errores = True
            continue

        if validador.errores:
            hay_errores = True
            for error in validador.errores:
                print(f"ERROR: {archivo}: {error}")
        else:
            print(f"OK: {archivo}")

    return 1 if hay_errores else 0


if __name__ == "__main__":
    sys.exit(main())
