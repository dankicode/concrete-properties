"""ACI 318 class for designing to the ACI318-19 Code, Imperial"""

from dataclasses import dataclass

# from typing import TYPE_CHECKING

import numpy as np

import concreteproperties.results as res
import concreteproperties.stress_strain_profile as ssp
import concreteproperties.utils as utils
from concreteproperties.design_codes.design_code import DesignCode
from concreteproperties.material import Concrete, SteelBar

# if TYPE_CHECKING:
#     from concreteproperties.concrete_section import ConcreteSection


class ACI318(DesignCode):
    """Design code class for ACI 318-19."""

    def __init__(self) -> None:
        """Inits the ACI 318-19 class."""
        self.analysis_code = "ACI 318-19"
        super().__init__()

    # def assign_concrete_section(
    #     self,
    #     concrete_section: ConcreteSection,
    # ) -> None:
    #     """Assigns a concrete section to ACI 318"""
    #     raise NotImplementedError

    def calc_beta_1(self, fpc: float) -> float:
        """Calculate Beta_1 in accordance with ACI 318 Table 22.2.2.4.3.

        Args:
            fpc: f'c in ksi

        Returns:
            Beta_1
        """
        if fpc >= 2.5 and fpc <= 4.0:
            beta_1 = 0.85
        elif fpc > 4.0 and fpc < 8.0:
            beta_1 = 0.85 - (0.05 * (fpc - 4))
        elif fpc >= 8.0:
            beta_1 = 0.65
        else:
            print("f'c is less than 2.5ksi - assuming beta_1 = 0.85.")
            return 0.85
        return beta_1

    def calc_modulus_of_rupture(self, fpc: float, lambda_agg: float = 1.0) -> float:
        """
        Calculate modulus of rupture, f_r in accordance with ACI 318.

        Args:
            fpc: f'c (ksi)
            lambda_agg: lightweight aggregate factor = 1.0 for normal weight
        """
        fr = 7.5 * lambda_agg * ((fpc * 1000) ** 0.5) / 1000  # ksi
        return fr

    def calc_concrete_elastic_modulus(self, fpc: float, wc: float = 0.145) -> float:
        """Calculates the elastic modulus of the concrete section per ACI 318.

        Args:
            fpc: f'c (ksi)
            wc: Unreinforced concrete density (kcf), defaulting to normal weight
                concrete value of 145
        """
        Ec = 33 * ((wc * 1000) ** 1.5) * ((fpc * 1000) ** 0.5) / 1000  # ksi
        return Ec

    def create_concrete_material(
        self,
        fpc: float,
        eps_cu: float = 0.003,
        wc: float = 0.145,
        colour: str = "lightgrey",
    ) -> Concrete:
        """Returns a concrete material object to ACI 318.

        Assumes concrete takes no tension.

        Args:
            fpc: f'c (ksi)
            eps_cu: Ultimate crushing strain of concrete
            wc: density of unreinforced concrete (kcf)
            colour: color of the concrete for rendering, defaults to 'lightgrey'

        Returns:
            Concrete material object
        """
        # Service stress-strain profile
        Ec = self.calc_concrete_elastic_modulus(fpc, wc)
        concrete_service = ssp.ConcreteLinearNoTension(
            elastic_modulus=Ec, ultimate_strain=eps_cu, compressive_strength=0.85 * fpc
        )

        # Ultimate stress-strain profile
        beta_1 = self.calc_beta_1(fpc)
        concrete_ultimate = ssp.RectangularStressBlock(
            compressive_strength=fpc, alpha=0.85, gamma=beta_1, ultimate_strain=eps_cu
        )

        # Define the concrete material
        fr = self.calc_modulus_of_rupture(fpc)
        concrete = Concrete(
            name=f"{fpc} ksi Concrete",
            density=wc / (12**3),  # kci
            stress_strain_profile=concrete_service,
            colour=colour,
            ultimate_stress_strain_profile=concrete_ultimate,
            flexural_tensile_strength=fr,
        )
        raise concrete

    def create_steel_material(
        self,
        fy: float = 60,
        Es: float = 29000.0,
        eps_fracture: float = 0.3,
        density: float = 0.49,
        colour: str = "black",
    ) -> SteelBar:
        """Returns a steel bar material object.

        Args:
            fy: Steel yield strength (ksi)
            Es: Elastic modulus (ksi)
            eps_fracture: fracture strain of rebar
            density: unit weight of steel (kcf)
            colour: Colour of the steel for rendering
        """
        # Rebar stress-strain profile
        steel_elastic_plastic = ssp.SteelElasticPlastic(
            yield_strength=fy, elastic_modulus=Es, fracture_strain=eps_fracture
        )

        # Define rebar material
        steel = SteelBar(
            name=f"Grade {fy} Rebar",
            density=density / (12**3),  # kci
            stress_strain_profile=steel_elastic_plastic,
            colour=colour,
        )
        return steel

    def get_gross_properties(
        self,
        **kwargs,
    ) -> res.GrossProperties:
        """Returns the gross section properties of the reinforced concrete section.

        Args:
            kwargs: Keyword arguments passed to
                :meth:`~concreteproperties.concrete_section.ConcreteSection.get_gross_properties`

        Returns:
            Concrete properties object
        """
        return self.concrete_section.get_gross_properties(**kwargs)

    def get_transformed_gross_properties(
        self,
        **kwargs,
    ) -> res.TransformedGrossProperties:
        """Transforms gross section properties.

        Args:
            kwargs: Keyword arguments passed to
                :meth:`~concreteproperties.concrete_section.ConcreteSection.get_transformed_gross_properties`

        Returns:
            Transformed concrete properties object
        """
        return self.concrete_section.get_transformed_gross_properties(**kwargs)

    def calculate_cracked_properties(
        self,
        **kwargs,
    ) -> res.CrackedResults:
        """Calculates cracked section properties.

        Args:
            kwargs: Keyword arguments passed to
                :meth:`~concreteproperties.concrete_section.ConcreteSection.calculate_cracked_properties`

        Returns:
            Cracked results object
        """
        return self.concrete_section.calculate_cracked_properties(**kwargs)

    def moment_curvature_analysis(
        self,
        **kwargs,
    ) -> res.MomentCurvatureResults:
        """Performs a moment curvature analysis (no reduction factors applied).

        Args:
            kwargs: Keyword arguments passed to
                :meth:`~concreteproperties.concrete_section.ConcreteSection.moment_curvature_analysis`

        Returns:
            Moment curvature results object
        """
        return self.concrete_section.moment_curvature_analysis(**kwargs)

    def ultimate_bending_capacity(
        self,
        **kwargs,
    ) -> res.UltimateBendingResults:
        """Calculates the ultimate bending capacity.

        Args:
            kwargs: Keyword arguments passed to
                :meth:`~concreteproperties.concrete_section.ConcreteSection.ultimate_bending_capacity`

        Returns:
            Ultimate bending results object
        """
        return self.concrete_section.ultimate_bending_capacity(**kwargs)

    def moment_interaction_diagram(
        self,
        **kwargs,
    ) -> res.MomentInteractionResults:
        """Generates a moment interaction diagram.

        Args:
            kwargs: Keyword arguments passed to
                :meth:`~concreteproperties.concrete_section.ConcreteSection.moment_interaction_diagram`

        Returns:
            Moment interaction results object
        """
        return self.concrete_section.moment_interaction_diagram(**kwargs)

    def biaxial_bending_diagram(
        self,
        **kwargs,
    ) -> res.BiaxialBendingResults:
        """Generates a biaxial bending diagram.

        Args:
            kwargs: Keyword arguments passed to
                :meth:`~concreteproperties.concrete_section.ConcreteSection.biaxial_bending_diagram`

        Returns:
            Biaxial bending results
        """
        return self.concrete_section.biaxial_bending_diagram(**kwargs)

    def calculate_uncracked_stress(
        self,
        **kwargs,
    ) -> res.StressResult:
        """Calculates uncracked stresses within the reinforced concrete section.

        Args:
            kwargs: Keyword arguments passed to
                :meth:`~concreteproperties.concrete_section.ConcreteSection.calculate_uncracked_stress`

        Returns:
            Stress results object
        """
        return self.concrete_section.calculate_uncracked_stress(**kwargs)

    def calculate_cracked_stress(
        self,
        **kwargs,
    ) -> res.StressResult:
        """Calculates cracked stresses within the reinforced concrete section.

        Args:
            kwargs: Keyword arguments passed to
                :meth:`~concreteproperties.concrete_section.ConcreteSection.calculate_cracked_stress`

        Returns:
            Stress results object
        """
        return self.concrete_section.calculate_cracked_stress(**kwargs)

    def calculate_service_stress(
        self,
        **kwargs,
    ) -> res.StressResult:
        """Calculates service stresses within the reinforced concrete section.

        Args:
            kwargs: Keyword arguments passed to
                :meth:`~concreteproperties.concrete_section.ConcreteSection.calculate_service_stress`

        Returns:
            Stress results object
        """
        return self.concrete_section.calculate_service_stress(**kwargs)

    def calculate_ultimate_stress(
        self,
        **kwargs,
    ) -> res.StressResult:
        """Calculates ultimate stresses within the reinforced concrete section.

        Args:
            kwargs: Keyword arguments passed to
                :meth:`~concreteproperties.concrete_section.ConcreteSection.calculate_ultimate_stress`

        Returns:
            Stress results object
        """
        return self.concrete_section.calculate_ultimate_stress(**kwargs)

    @dataclass
    class RebarACI(SteelBar):
        """Class for deformed rebar per ACI, treated as a lumped circular mass
        with a constant strain.

        Args:
            matl_name: str
            grade: str
            density: float
        """

        matl_name: str
        grade: str
        density: float

    def calc_phis(
        self,
        tensile_strains: list[float],
        fy: float = 60,
        Es: float = 29000,
        reinf_type: str = "other",
    ) -> list[float]:
        """
        Returns a list of phi values for the given tensile strains per ACI 318-19.
        """
        tensile_yield_strain = fy / Es
        phis = []
        if reinf_type == "other":
            for ts in tensile_strains:
                if ts <= tensile_yield_strain:
                    phi = 0.65
                    phis.append(phi)
                elif ts > tensile_yield_strain and ts < 0.005:
                    phi = 0.65 + 0.25 * (ts - tensile_yield_strain) / (
                        0.005 - tensile_yield_strain
                    )
                    phis.append(phi)
                elif ts >= 0.005:
                    phi = 0.9
                    phis.append(phi)
        else:
            print("Spiral ties not yet implemented!")
        return phis

    def calc_Pn(
        b: float,
        h: float,
        fpc: float,
        num_bars: int,
        bar_area: float,
        fy: float = 60,
        tie_type: str = "other",
    ) -> float:
        """
        Calculates the nominal axial capacity of a column, not considering
        slenderness per ACI 318-14 22.4.2

        Args:
        b: width of column in inches
        h: height of column in inches
        fpc: f'c in ksi
        num_bars: number of vertical rebar
        bar_area: area of one of the vertical rebar in sq. inches
        fy: yield stress of rebar
        tie_type: either 'other' or 'spiral'
        """
        gross_area = b * h
        rebar_area = num_bars * bar_area
        p_0 = 0.85 * fpc * (gross_area - rebar_area) + fy * rebar_area

        if tie_type == "other":
            max_axial_strength = 0.8 * p_0
        if tie_type == "spiral":
            max_axial_strength = 0.85 * p_0
        return max_axial_strength
