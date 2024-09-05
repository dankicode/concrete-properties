from dataclasses import dataclass

REBAR = {
    "#3": {"As": 0.11, "d_bar": 0.375, "plf": 0.375},
    "#4": {"As": 0.20, "d_bar": 0.5, "plf": 0.668},
    "#5": {"As": 0.31, "d_bar": 0.625, "plf": 1.043},
    "#6": {"As": 0.44, "d_bar": 0.75, "plf": 1.502},
    "#7": {"As": 0.60, "d_bar": 0.875, "plf": 2.044},
    "#8": {"As": 0.79, "d_bar": 1.00, "plf": 2.67},
    "#9": {"As": 1.00, "d_bar": 1.128, "plf": 3.4},
    "#10": {"As": 1.27, "d_bar": 1.27, "plf": 4.303},
    "#11": {"As": 1.56, "d_bar": 1.41, "plf": 5.313},
    "#14": {"As": 2.25, "d_bar": 1.693, "plf": 7.65},
    "#18": {"As": 4.00, "d_bar": 2.257, "plf": 13.6},
}


@dataclass
class Rebar:
    As: float
    d_bar: float
    plf: float


N3 = Rebar(As=0.11, d_bar=0.375, plf=0.376)
N4 = Rebar(As=0.2, d_bar=0.5, plf=0.668)
N5 = Rebar(As=0.31, d_bar=0.625, plf=1.043)
N6 = Rebar(As=0.44, d_bar=0.75, plf=1.502)
N7 = Rebar(As=0.6, d_bar=0.875, plf=2.044)
N8 = Rebar(As=0.79, d_bar=1.0, plf=2.67)
N9 = Rebar(As=1.0, d_bar=1.128, plf=3.4)
N10 = Rebar(As=1.27, d_bar=1.27, plf=4.303)
N11 = Rebar(As=1.56, d_bar=1.41, plf=5.313)
N14 = Rebar(As=2.25, d_bar=1.693, plf=7.65)
N18 = Rebar(As=4.00, d_bar=2.257, plf=13.6)
N20 = Rebar(As=4.91, d_bar=2.5, plf=16.63)
