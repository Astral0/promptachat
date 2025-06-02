"""
Service pour la gestion des variables Cockpit.
"""
from typing import List, Dict, Any
from backend.models import CockpitVariable

class CockpitService:
    """Service for managing Cockpit variables."""
    
    def __init__(self):
        # Dictionnaire des variables Cockpit avec étiquettes conviviales
        self.cockpit_variables = {
            "nom_entreprise": "Nom de l'entreprise",
            "secteur_activite": "Secteur d'activité", 
            "taille_entreprise": "Taille de l'entreprise",
            "chiffre_affaires": "Chiffre d'affaires",
            "nb_employees": "Nombre d'employés",
            "pays_siege": "Pays du siège social",
            "ville_siege": "Ville du siège social",
            "forme_juridique": "Forme juridique",
            "num_siret": "Numéro SIRET",
            "num_siren": "Numéro SIREN",
            "code_naf": "Code NAF",
            "date_creation": "Date de création",
            "dirigeant_principal": "Dirigeant principal",
            "directeur_achats": "Directeur des achats",
            "contact_achats": "Contact achats",
            "email_achats": "Email achats", 
            "telephone_achats": "Téléphone achats",
            "adresse_facturation": "Adresse de facturation",
            "adresse_livraison": "Adresse de livraison",
            "methode_paiement_pref": "Méthode de paiement préférée",
            "delai_paiement_std": "Délai de paiement standard",
            "devise_principale": "Devise principale",
            "budget_achats_annuel": "Budget achats annuel",
            "nb_fournisseurs_actifs": "Nombre de fournisseurs actifs",
            "fournisseur_principal": "Fournisseur principal",
            "categories_achats": "Catégories d'achats",
            "politique_rse": "Politique RSE",
            "certifications_qualite": "Certifications qualité",
            "objectifs_dev_durable": "Objectifs développement durable",
            "contraintes_reglementaires": "Contraintes réglementaires",
            "exigences_conformite": "Exigences de conformité",
            "niveau_risque_fournisseur": "Niveau de risque fournisseur",
            "procedures_audit": "Procédures d'audit",
            "systeme_erp": "Système ERP",
            "outils_achats": "Outils achats utilisés",
            "processus_validation": "Processus de validation",
            "workflows_approbation": "Workflows d'approbation",
            "kpi_achats": "KPI achats suivis",
            "frequence_reporting": "Fréquence de reporting",
            "objectifs_reduction_couts": "Objectifs de réduction des coûts",
            "strategie_negociation": "Stratégie de négociation",
            "politique_diversite_fournisseurs": "Politique de diversité fournisseurs",
            "criteres_selection_fournisseurs": "Critères de sélection fournisseurs",
            "seuils_approbation": "Seuils d'approbation",
            "delegation_signature": "Délégation de signature",
            "contrats_cadres": "Contrats cadres en place",
            "accords_groupe": "Accords groupe",
            "partenariats_strategiques": "Partenariats stratégiques",
            "innovations_recherchees": "Innovations recherchées",
            "projets_transformation": "Projets de transformation",
            "enjeux_prioritaires": "Enjeux prioritaires",
            "risques_identifies": "Risques identifiés",
            "plan_continuite": "Plan de continuité",
            "veille_marche": "Veille marché",
            "benchmark_concurrentiel": "Benchmark concurrentiel",
            "tendances_secteur": "Tendances du secteur",
            "evolution_prix": "Évolution des prix",
            "nouveaux_fournisseurs": "Nouveaux fournisseurs",
            "technologies_emergentes": "Technologies émergentes",
            "reglementation_evolution": "Évolution réglementaire",
            "date_analyse": "Date d'analyse",
            "analyseur": "Analyseur",
            "version_document": "Version du document",
            "statut_validation": "Statut de validation",
            "prochaine_revision": "Prochaine révision",
            "niveau_confidentialite": "Niveau de confidentialité"
        }
    
    def get_all_variables(self) -> List[CockpitVariable]:
        """Récupère toutes les variables Cockpit disponibles."""
        return [
            CockpitVariable(
                key=key,
                label=label,
                description=f"Variable Cockpit : {label}"
            )
            for key, label in self.cockpit_variables.items()
        ]
    
    def get_variable_by_key(self, key: str) -> CockpitVariable:
        """Récupère une variable Cockpit par sa clé."""
        if key in self.cockpit_variables:
            return CockpitVariable(
                key=key,
                label=self.cockpit_variables[key],
                description=f"Variable Cockpit : {self.cockpit_variables[key]}"
            )
        return None
    
    def get_variables_dict(self) -> Dict[str, str]:
        """Récupère le dictionnaire complet des variables."""
        return self.cockpit_variables.copy()
    
    def validate_variable_keys(self, keys: List[str]) -> List[str]:
        """Valide une liste de clés de variables et retourne celles qui sont valides."""
        return [key for key in keys if key in self.cockpit_variables]
    
    def format_variables_for_prompt(self, variables: List[str]) -> str:
        """Formate les variables pour affichage dans un prompt."""
        if not variables:
            return ""
        
        formatted = []
        for var in variables:
            if var in self.cockpit_variables:
                formatted.append(f"{{{var}}} - {self.cockpit_variables[var]}")
            else:
                formatted.append(f"{{{var}}} - Variable personnalisée")
        
        return "\n".join(formatted)
    
    def extract_cockpit_variables_from_content(self, content: str) -> List[str]:
        """Extrait automatiquement les variables Cockpit présentes dans le contenu d'un prompt."""
        import re
        
        # Recherche de toutes les variables {variable_name}
        pattern = r'\{([^}]+)\}'
        found_vars = re.findall(pattern, content)
        
        # Filtre pour ne garder que les variables Cockpit valides
        cockpit_vars = []
        for var in found_vars:
            if var in self.cockpit_variables:
                cockpit_vars.append(var)
        
        return list(set(cockpit_vars))  # Supprime les doublons
    
    def check_uses_cockpit_data(self, variables: List[str]) -> bool:
        """Vérifie si la liste de variables contient au moins une variable Cockpit."""
        return any(var in self.cockpit_variables for var in variables)