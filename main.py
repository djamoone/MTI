from module import Module
from unit import Unit
from semester import Semester


# ==========================================
# Helpers
# ==========================================

def display_semester(semester):
    """Display the results of a semester (modules, units, totals)."""
    print("Modules:")

    all_modules = [m for unit in semester.units for m in unit._modules]

    for module in all_modules:
        print(
            module.name,
            "-",
            module.title,
            "| Mode:", module.teaching_mode,
            "| Average:", module.calculate_average(),
            "| Credits:", module.calculate_credits()
        )

    print("\nUnits:")
    for unit in semester.units:
        print(
            unit.name,
            "-",
            unit.title,
            "| Average:", unit.calculate_average(),
            "| Credits:", unit.calculate_credits()
        )

    print("\n" + semester.name, "Average:", semester.calculate_average())
    print(semester.name, "Credits:", semester.calculate_credits())


def build_semester_1():
    """Build Semester 1 from the official curriculum table."""
    s1 = Semester("S1", "Premier Semestre")

    # ---- UE Fondamentale 1 (UF11) ----
    uf11 = Unit("UF11", "Unite Fondamentale 1")

    f111 = Module(
        "F111", "Reseaux des couches basses",
        coef=3, credit=6,
        hours_lecture=1.5, hours_td=1.5, hours_tp=1.5
    )
    f112 = Module(
        "F112", "Algorithmique Avancee et Complexite",
        coef=2, credit=4,
        hours_lecture=1.5, hours_td=1.5, hours_tp=1.5
    )

    # Example grades for S1
    f111.set_grade(tp=12, td=13, exam=14)
    f112.set_grade(tp=13, td=12, exam=15)

    uf11.add_module(f111)
    uf11.add_module(f112)
    s1.add_unit(uf11)

    # ---- UE Fondamentale 2 (UF12) ----
    uf12 = Unit("UF12", "Unite Fondamentale 2")

    f121 = Module(
        "F121", "Systeme d'Exploitation",
        coef=2, credit=4,
        hours_lecture=1.5, hours_td=1.5, hours_tp=1.5
    )
    f122 = Module(
        "F122", "Architectures Modernes des Systemes Informatiques",
        coef=2, credit=4,
        hours_lecture=1.5, hours_td=1.5, hours_tp=1.5
    )

    f121.set_grade(td=12, exam=14)
    f122.set_grade(tp=11, exam=13)

    uf12.add_module(f121)
    uf12.add_module(f122)
    s1.add_unit(uf12)

    # ---- UE Methodologique (UM11) ----
    um11 = Unit("UM11", "Unite Methodologique 1")

    m111 = Module(
        "M111", "Architecture et Administration des Bases de Donnees",
        coef=2, credit=4,
        hours_lecture=1.5, hours_td=1.5, hours_tp=1.5
    )
    m112 = Module(
        "M112", "Methodes et Technologies de l'Implementation",
        coef=3, credit=5,
        hours_lecture=1.5, hours_td=1.5, hours_tp=1.5
    )

    m111.set_grade(td=10, exam=12)
    m112.set_grade(tp=14, exam=15)

    um11.add_module(m111)
    um11.add_module(m112)
    s1.add_unit(um11)

    # ---- UE Decouverte (UD11) ----
    ud11 = Unit("UD11", "Unite Decouverte 1")

    d111 = Module(
        "D111", "Systemes de Communication Vocaux et Videos",
        coef=2, credit=2,
        hours_lecture=1.5, hours_td=1.5, hours_tp=1.5
    )
    d111.set_grade(td=13, exam=14)

    ud11.add_module(d111)
    s1.add_unit(ud11)

    # ---- UE Transversale (UT11) ----
    ut11 = Unit("UT11", "Unite Transversale 1")

    t111 = Module(
        "T111", "Cloud Computing",
        coef=1, credit=1,
        hours_lecture=1.5, hours_td=0, hours_tp=0,
        teaching_mode="Distanciel",
        continous_percent=0,
        exam_percent=100
    )
    # Distanciel module: 100% exam, no continuous assessment
    t111.set_grade(exam=16)

    ut11.add_module(t111)
    s1.add_unit(ut11)

    return s1


def build_semester_2():
    """Build Semester 2 from the official curriculum table."""
    s2 = Semester("S2", "Deuxieme Semestre")

    # ---- UE Fondamentale 1 (UF21) ----
    uf21 = Unit("UF21", "Unite Fondamentale 1")

    f211 = Module(
        "F211", "Les Middlewares pour les Systemes Repartis",
        coef=3, credit=6,
        hours_lecture=1.5, hours_td=1.5, hours_tp=1.5
    )
    f212 = Module(
        "F212", "Modelisation et Architectures Logicielles",
        coef=2, credit=4,
        hours_lecture=1.5, hours_td=1.5, hours_tp=1.5
    )

    # Example grades for S2
    f211.set_grade(tp=12, td=12, exam=14)
    f212.set_grade(tp=13, td=13, exam=15)

    uf21.add_module(f211)
    uf21.add_module(f212)
    s2.add_unit(uf21)

    # ---- UE Fondamentale 2 (UF22) ----
    uf22 = Unit("UF22", "Unite Fondamentale 2")

    f221 = Module(
        "F221", "Reseaux de la Couche IP",
        coef=3, credit=6,
        hours_lecture=1.5, hours_td=1.5, hours_tp=1.5
    )
    f222 = Module(
        "F222", "Introduction au Machine Learning",
        coef=2, credit=4,
        hours_lecture=1.5, hours_td=1.5, hours_tp=1.5
    )

    f221.set_grade(tp=11, td=11, exam=13)
    f222.set_grade(tp=14, td=14, exam=16)

    uf22.add_module(f221)
    uf22.add_module(f222)
    s2.add_unit(uf22)

    # ---- UE Methodologique (UM21) ----
    um21 = Unit("UM21", "Unite Methodologique 1")

    m211 = Module(
        "M211", "Infographie",
        coef=2, credit=3,
        hours_lecture=1.5, hours_td=0, hours_tp=1.5
    )
    m212 = Module(
        "M212", "Gestion de l'Incertitude",
        coef=2, credit=3,
        hours_lecture=1.5, hours_td=1.5, hours_tp=0
    )

    m211.set_grade(tp=12, exam=13)
    m212.set_grade(td=11, exam=14)

    um21.add_module(m211)
    um21.add_module(m212)
    s2.add_unit(um21)

    # ---- UE Decouverte (UD21) ----
    ud21 = Unit("UD21", "Unite Decouverte 1")

    d211 = Module(
        "D211", "Internet of Things",
        coef=2, credit=3,
        hours_lecture=1.5, hours_td=0, hours_tp=1.5
    )
    d211.set_grade(tp=15, exam=16)

    ud21.add_module(d211)
    s2.add_unit(ud21)

    # ---- UE Transversale (UT21) ----
    ut21 = Unit("UT21", "Unite Transversale 1")

    t211 = Module(
        "T211", "Cybercriminalite",
        coef=1, credit=1,
        hours_lecture=1.5, hours_td=0, hours_tp=0,
        teaching_mode="Distanciel",
        continous_percent=0,
        exam_percent=100
    )
    # Distanciel module: 100% exam, no continuous assessment
    t211.set_grade(exam=15)

    ut21.add_module(t211)
    s2.add_unit(ut21)

    return s2


def main():
    # ==========================================
    # SEMESTER 1 (S1)
    # ==========================================
    print("\n========== SEMESTER 1 ==========\n")

    s1 = build_semester_1()
    display_semester(s1)

    # ==========================================
    # SEMESTER 2 (S2)
    # ==========================================
    print("\n========== SEMESTER 2 ==========\n")

    s2 = build_semester_2()
    display_semester(s2)


if __name__ == "__main__":
    main()
