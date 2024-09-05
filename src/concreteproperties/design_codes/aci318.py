"""ACI 318 class for designing to the ACI318-19 Code, Imperial"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

import concreteproperties.results as res
import concreteproperties.stress_strain_profile as ssp
import concreteproperties.utils as utils
from concreteproperties.design_codes.design_code import DesignCode
from concreteproperties.material import Concrete, SteelBar

if TYPE_CHECKING:
    from concreteproperties.concrete_section import ConcreteSection


class ACI318(DesignCode):
    """Design code class for ACI 318-19."""

    def __init__(self) -> None:
        """Inits the ACI 318-19 class."""
        super().__init__()

    def assign_concrete_section(
        self,
        concrete_section: ConcreteSection,
    ) -> None:
        """Assigns a concrete section to ACI 318"""
        raise NotImplementedError

    def create_concrete_material(
        self,
        compressive_strength: float,
        ultimate_strain: float = 0.003,
        density: float = 0.145,
        colour: str = "lightgrey",
    ) -> Concrete:
        """Returns a concrete material object to ACI 318.

        Args:
            compressive_strength: f'c (ksi)
            ultimate_strain: Maximum concrete compressive strain at concrete
                crushing
            density: density of unreinforced concrete (kcf)
            colour: color of the concrete for rendering, defaults to 'lightgrey'

        Returns:
            Concrete material object
        """
        raise NotImplementedError

    def create_steel_material(
        self,
        yield_strength: float,
        colour: str = "grey",
    ) -> SteelBar:
        """Returns a steel bar material object.

        List assumptions of material properties here...

        Args:
            yield_strength: Steel yield strength
            colour: Colour of the steel for rendering

        Raises:
            NotImplementedError: If this method has not been implemented by the child
                class
        """
        raise NotImplementedError

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

    def calc_phi(
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
