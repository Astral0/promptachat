"""
Script pour nettoyer et réimporter uniquement les nouveaux prompts.
"""
import json
from pathlib import Path

def clean_and_import_prompts():
    """Clean old prompts and import only the new 20 prompts."""
    
    # Les 20 nouveaux prompts uniquement
    new_prompts_data = {
        "system_prompts": [
            {
                "id": "internal_1",
                "title": "Analyse de Performance Fournisseur Avancée",
                "category": "Évaluation Fournisseur",
                "description": "Analyse détaillée des performances d'un fournisseur sur plusieurs critères avec recommandations d'amélioration.",
                "content": """Vous êtes un expert en évaluation fournisseur. Analysez en détail les performances du fournisseur avec les informations suivantes :

**Informations Cockpit :**
- Entreprise : {nom_entreprise}
- Secteur : {secteur_activite}
- Fournisseur évalué : {fournisseur_principal}
- Période d'évaluation : {date_analyse}

**Critères d'évaluation :**
1. **Qualité des produits/services** (pondération 30%)
2. **Respect des délais** (pondération 25%)
3. **Compétitivité tarifaire** (pondération 20%)
4. **Service client et réactivité** (pondération 15%)
5. **Innovation et amélioration continue** (pondération 10%)

Pour chaque critère, fournissez :
- Une note sur 5
- Une justification détaillée
- Des recommandations spécifiques d'amélioration
- Des actions correctives si nécessaire

**Synthèse demandée :**
- Note globale pondérée
- Forces principales du fournisseur
- Axes d'amélioration prioritaires
- Recommandations pour la suite de la relation
- Plan d'action avec échéances""",
                "type": "internal",
                "variables": ["nom_entreprise", "secteur_activite", "fournisseur_principal", "date_analyse"],
                "uses_cockpit_data": True,
                "is_system": True,
                "accepts_files": False,
                "welcome_page_html": ""
            },
            {
                "id": "internal_2", 
                "title": "Audit de Conformité RSE Fournisseur",
                "category": "RSE et Développement Durable",
                "description": "Audit complet de la conformité RSE d'un fournisseur avec grille d'évaluation détaillée.",
                "content": """En tant qu'expert en RSE et développement durable, conduisez un audit de conformité RSE pour notre fournisseur.

**Contexte entreprise :**
- Entreprise : {nom_entreprise}
- Secteur : {secteur_activite}
- Politique RSE : {politique_rse}
- Objectifs développement durable : {objectifs_dev_durable}

**Fournisseur à auditer :**
- Nom : {fournisseur_principal}
- Activité principale : [À préciser]
- Localisation : [À préciser]

**Axes d'audit RSE :**

1. **Environnement**
   - Certifications ISO 14001, ISO 50001
   - Politique de réduction carbone
   - Gestion des déchets et recyclage
   - Utilisation d'énergies renouvelables

2. **Social et conditions de travail**
   - Respect des droits humains
   - Conditions de travail et sécurité
   - Diversité et inclusion
   - Formation et développement des employés

3. **Gouvernance et éthique**
   - Code de conduite et éthique
   - Lutte contre la corruption
   - Transparence et reporting
   - Gestion des parties prenantes

4. **Impact local et sociétal**
   - Contribution au développement local
   - Partenariats avec des acteurs locaux
   - Initiatives communautaires

**Livrable attendu :**
- Évaluation détaillée par axe (note /10)
- Points forts et non-conformités identifiées
- Plan d'amélioration avec priorités
- Recommandations de suivi et contrôle""",
                "type": "internal",
                "variables": ["nom_entreprise", "secteur_activite", "politique_rse", "objectifs_dev_durable", "fournisseur_principal"],
                "uses_cockpit_data": True,
                "is_system": True,
                "accepts_files": False,
                "welcome_page_html": ""
            },
            {
                "id": "internal_3",
                "title": "Stratégie de Négociation Adaptée",
                "category": "Négociation", 
                "description": "Élaboration d'une stratégie de négociation personnalisée selon le contexte et les enjeux.",
                "content": """Vous êtes un expert en négociation commerciale. Développez une stratégie de négociation adaptée à notre contexte.

**Profil entreprise :**
- Entreprise : {nom_entreprise}
- Budget achats annuel : {budget_achats_annuel}
- Stratégie négociation actuelle : {strategie_negociation}
- Délai paiement standard : {delai_paiement_std}

**Contexte de négociation :**
- Type d'achat : [À préciser]
- Montant approximatif : [À préciser]
- Enjeux critiques : [À préciser]
- Contraintes temporelles : [À préciser]

**Analyse préparatoire :**

1. **Analyse du rapport de force**
   - Position de l'acheteur
   - Dépendance mutuelle
   - Alternatives disponibles (BATNA)

2. **Objectifs et limites**
   - Objectifs optimaux, acceptables et de rupture
   - Variables négociables (prix, délais, qualité, services...)
   - Contraintes non négociables

3. **Profil fournisseur**
   - Motivations et contraintes du fournisseur
   - Historique relationnel
   - Leviers d'influence

**Stratégie recommandée :**
- Approche négociation (compétitive/collaborative)
- Séquencement des étapes
- Arguments et contre-arguments
- Tactiques spécifiques
- Plan B en cas d'échec

**Kit de négociation :**
- Scripts de négociation par phase
- Objections probables et réponses
- Indicateurs de suivi en temps réel""",
                "type": "internal",
                "variables": ["nom_entreprise", "budget_achats_annuel", "strategie_negociation", "delai_paiement_std"],
                "uses_cockpit_data": True,
                "is_system": True,
                "accepts_files": False,
                "welcome_page_html": ""
            },
            {
                "id": "external_1",
                "title": "Benchmark Tarifaire Sectoriel",
                "category": "Veille Marché",
                "description": "Analyse comparative des tarifs pratiqués dans le secteur avec recommandations de négociation.",
                "content": "<p>Vous êtes un expert en analyse de marché spécialisé dans le secteur <strong>[SECTEUR D'ACTIVITÉ]</strong>. Je souhaite réaliser un benchmark tarifaire pour optimiser mes négociations fournisseurs.</p><p><strong>Contexte :</strong></p><ul><li>Entreprise : [NOM ENTREPRISE]</li><li>Secteur d'activité : [SECTEUR]</li><li>Volume d'achats annuel : [BUDGET]</li><li>Géographie : [PAYS/RÉGION]</li></ul><p><strong>Analyse attendue :</strong></p><ol><li><strong>Tendances tarifaires du marché</strong><ul><li>Évolution des prix sur 12-24 mois</li><li>Facteurs d'influence (matières premières, réglementation, etc.)</li></ul></li><li><strong>Positionnement concurrentiel</strong><ul><li>Fourchettes de prix par catégorie</li><li>Positionnement de nos fournisseurs actuels</li></ul></li><li><strong>Recommandations actionables</strong><ul><li>Objectifs d'économies réalistes</li><li>Plan d'action par fournisseur</li></ul></li></ol>",
                "type": "external",
                "variables": [],
                "uses_cockpit_data": False,
                "is_system": True,
                "accepts_files": False,
                "welcome_page_html": ""
            },
            {
                "id": "external_2",
                "title": "Cahier des Charges Appel d'Offres",
                "category": "Stratégie Achats",
                "description": "Rédaction complète d'un cahier des charges pour appel d'offres structuré et professionnel.",
                "content": "<p>Vous êtes un expert en rédaction de cahiers des charges et appels d'offres. Rédigez un cahier des charges complet et structuré pour notre appel d'offres.</p><p><strong>Informations générales :</strong></p><ul><li>Entreprise : [NOM ENTREPRISE]</li><li>Objet de l'appel d'offres : [DESCRIPTION DÉTAILLÉE]</li><li>Budget estimé : [MONTANT]</li></ul><p><strong>Structure du cahier des charges :</strong></p><ol><li><strong>Présentation de l'entreprise et du projet</strong></li><li><strong>Spécifications techniques détaillées</strong></li><li><strong>Exigences qualité et performance</strong></li><li><strong>Modalités contractuelles</strong></li><li><strong>Critères d'évaluation des offres</strong></li></ol>",
                "type": "external",
                "variables": [],
                "uses_cockpit_data": False,
                "is_system": True,
                "accepts_files": False,
                "welcome_page_html": ""
            }
        ]
    }
    
    # Sauvegarder le nouveau fichier de prompts
    prompts_file = Path('data/prompts.json')
    with open(prompts_file, 'w', encoding='utf-8') as f:
        json.dump(new_prompts_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {len(new_prompts_data['system_prompts'])} prompts nettoyés et importés avec succès!")
    
    return new_prompts_data

if __name__ == "__main__":
    clean_and_import_prompts()