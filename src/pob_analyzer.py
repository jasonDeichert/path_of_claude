"""Analyze Path of Building codes to extract build information."""

import base64
import zlib
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SkillGem:
    """Represents a skill gem setup."""
    name: str
    level: int
    quality: int
    enabled: bool


@dataclass
class SkillGroup:
    """Represents a linked gem group."""
    slot: str
    gems: List[SkillGem]
    enabled: bool

    @property
    def main_skill(self) -> Optional[str]:
        """Get the main active skill from this group."""
        for gem in self.gems:
            if gem.enabled and not self._is_support(gem.name):
                return gem.name
        return None

    @staticmethod
    def _is_support(gem_name: str) -> bool:
        """Check if a gem is a support gem."""
        support_keywords = ['Support', 'Damage', 'Faster', 'Greater', 'Increased',
                          'Added', 'Multiple', 'Concentrated', 'Awakened']
        return any(keyword in gem_name for keyword in support_keywords)


@dataclass
class POBAnalysis:
    """Complete analysis of a POB build."""
    character_level: int
    ascendancy: str
    passive_nodes: Set[int]
    keystones: List[str]
    skill_groups: List[SkillGroup]
    main_skill: Optional[str]
    notable_passives: List[str]

    def get_skill_links(self) -> Dict[str, List[str]]:
        """Get all skill setups with their support gems."""
        links = {}
        for group in self.skill_groups:
            if group.main_skill and group.enabled:
                links[group.main_skill] = [gem.name for gem in group.gems if gem.enabled]
        return links


class POBAnalyzer:
    """Analyzes Path of Building codes."""

    # Notable keystones to track
    KEYSTONES = {
        'Elemental Overload', 'Resolute Technique', 'Avatar of Fire',
        'Acrobatics', 'Phase Acrobatics', 'Mind Over Matter',
        'Ghost Dance', 'Divine Shield', "Zealot's Oath",
        'Chaos Inoculation', 'Eldritch Battery', 'Blood Magic',
        'Unwavering Stance', 'Iron Reflexes', 'Ancestral Bond',
        'Elemental Equilibrium', 'Point Blank', 'Perfect Agony',
        'Crimson Dance', 'Ghost Reaver', 'Vaal Pact',
        'Necromantic Aegis', 'Arrow Dancing', 'Supremacy',
        'Divine Flesh', 'Glancing Blows', 'The Agnostic',
        'Magebane', 'Runebinder', 'Call to Arms'
    }

    def __init__(self):
        """Initialize analyzer."""
        pass

    def decode_pob_code(self, pob_code: str) -> str:
        """
        Decode a POB code to XML string.

        Args:
            pob_code: Base64-encoded POB import code

        Returns:
            XML string of the build
        """
        # Remove whitespace and URL encoding
        pob_code = pob_code.strip().replace('%20', '').replace(' ', '').replace('\n', '')

        # Decode base64
        compressed = base64.b64decode(pob_code)

        # Try standard zlib first, then raw deflate
        try:
            xml_bytes = zlib.decompress(compressed)
        except zlib.error:
            # Try raw deflate (no zlib header)
            xml_bytes = zlib.decompress(compressed, -zlib.MAX_WBITS)

        # Convert to string
        xml_str = xml_bytes.decode('utf-8')

        return xml_str

    def analyze_pob_code(self, pob_code: str) -> POBAnalysis:
        """
        Analyze a POB code and extract build information.

        Args:
            pob_code: Base64-encoded POB import code

        Returns:
            POBAnalysis with extracted build data
        """
        xml_str = self.decode_pob_code(pob_code)
        root = ET.fromstring(xml_str)

        # Extract basic info
        build = root.find('Build')
        level = int(build.get('level', 1)) if build is not None else 1
        class_name = build.get('className', 'Unknown') if build is not None else 'Unknown'
        ascend_name = build.get('ascendClassName', '') if build is not None else ''

        # Extract passive tree
        tree = root.find('Tree')
        passive_nodes = set()
        if tree is not None:
            spec = tree.find('Spec')
            if spec is not None:
                nodes_str = spec.get('nodes', '')
                if nodes_str:
                    passive_nodes = {int(n) for n in nodes_str.split(',')}

        # Extract keystones and notables
        keystones = []
        notable_passives = []
        # Note: We'd need the passive tree JSON to map node IDs to names
        # For now, we'll extract what we can from other sources

        # Extract skills
        skill_groups = self._extract_skills(root)

        # Determine main skill
        main_skill = None
        for group in skill_groups:
            if group.enabled and group.main_skill:
                main_skill = group.main_skill
                break

        return POBAnalysis(
            character_level=level,
            ascendancy=ascend_name or class_name,
            passive_nodes=passive_nodes,
            keystones=keystones,  # Empty for now without passive tree data
            skill_groups=skill_groups,
            main_skill=main_skill,
            notable_passives=notable_passives
        )

    def _extract_skills(self, root: ET.Element) -> List[SkillGroup]:
        """Extract skill gem setups from POB XML."""
        skill_groups = []

        skills = root.find('Skills')
        if skills is None:
            return skill_groups

        for skill_set in skills.findall('SkillSet'):
            # Get active skill set
            active = skill_set.get('active', 'true') == 'true'

            for skill in skill_set.findall('Skill'):
                enabled = skill.get('enabled', 'true') == 'true'
                slot = skill.get('slot', 'Unknown')

                gems = []
                for gem in skill.findall('Gem'):
                    gem_name = gem.get('nameSpec', '')
                    if not gem_name:
                        continue

                    gem_level = int(gem.get('level', 1))
                    gem_quality = int(gem.get('quality', 0))
                    gem_enabled = gem.get('enabled', 'true') == 'true'

                    gems.append(SkillGem(
                        name=gem_name,
                        level=gem_level,
                        quality=gem_quality,
                        enabled=gem_enabled
                    ))

                if gems:
                    skill_groups.append(SkillGroup(
                        slot=slot,
                        gems=gems,
                        enabled=enabled and active
                    ))

        return skill_groups

    def analyze_pob_file(self, filepath: str) -> POBAnalysis:
        """
        Analyze a POB code from a file.

        Args:
            filepath: Path to file containing POB code

        Returns:
            POBAnalysis with extracted build data
        """
        with open(filepath, 'r') as f:
            pob_code = f.read().strip()

        return self.analyze_pob_code(pob_code)

    def compare_trees(self, analysis1: POBAnalysis, analysis2: POBAnalysis) -> Dict[str, Set[int]]:
        """
        Compare two passive trees.

        Args:
            analysis1: First build analysis
            analysis2: Second build analysis

        Returns:
            Dict with 'common', 'only_first', 'only_second' node sets
        """
        return {
            'common': analysis1.passive_nodes & analysis2.passive_nodes,
            'only_first': analysis1.passive_nodes - analysis2.passive_nodes,
            'only_second': analysis2.passive_nodes - analysis1.passive_nodes
        }

    def extract_common_tree(self, analyses: List[POBAnalysis]) -> Set[int]:
        """
        Extract common passive nodes across multiple builds.

        Args:
            analyses: List of build analyses

        Returns:
            Set of node IDs common to all builds
        """
        if not analyses:
            return set()

        common = analyses[0].passive_nodes.copy()
        for analysis in analyses[1:]:
            common &= analysis.passive_nodes

        return common


def main():
    """Example usage of POB analyzer."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m src.pob_analyzer <pob_file>")
        sys.exit(1)

    analyzer = POBAnalyzer()

    filepath = sys.argv[1]
    print(f"Analyzing: {filepath}")
    print("=" * 60)

    analysis = analyzer.analyze_pob_file(filepath)

    print(f"Level: {analysis.character_level}")
    print(f"Ascendancy: {analysis.ascendancy}")
    print(f"Main Skill: {analysis.main_skill}")
    print(f"Passive Nodes: {len(analysis.passive_nodes)}")
    print(f"\nSkill Setups:")

    for skill, gems in analysis.get_skill_links().items():
        print(f"\n{skill}:")
        for gem in gems:
            print(f"  - {gem}")


if __name__ == '__main__':
    main()
