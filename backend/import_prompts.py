"""
Script pour importer les nouveaux prompts fournis par l'utilisateur.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

def import_new_prompts():
    """Import new prompts from the provided JSON data."""
    
    # Les 20 nouveaux prompts fournis par l'utilisateur
    new_prompts = {
        "internal_prompts": [
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
                "is_system": True
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
                "is_system": True
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
                "is_system": True
            },
            {
                "id": "internal_4",
                "title": "Analyse de Risque Fournisseur Multi-Critères",
                "category": "Gestion des Risques",
                "description": "Évaluation complète des risques associés à un fournisseur avec matrice de criticité.",
                "content": """En tant qu'expert en gestion des risques fournisseurs, effectuez une analyse de risque complète.

**Contexte organisationnel :**
- Entreprise : {nom_entreprise}
- Secteur d'activité : {secteur_activite}
- Niveau de risque fournisseur actuel : {niveau_risque_fournisseur}
- Procédures d'audit : {procedures_audit}

**Fournisseur à analyser :**
- Nom : {fournisseur_principal}
- Criticité pour l'activité : [À préciser]
- Montant annuel : [À préciser]

**Dimensions d'analyse des risques :**

1. **Risques financiers**
   - Stabilité financière
   - Solvabilité et liquidité
   - Dépendance économique

2. **Risques opérationnels**
   - Capacité de production
   - Qualité et conformité
   - Délais et fiabilité de livraison

3. **Risques stratégiques**
   - Dépendance mutuelle
   - Concentration du portefeuille
   - Évolution du marché

4. **Risques géopolitiques et réglementaires**
   - Stabilité pays/région
   - Évolution réglementaire
   - Contraintes import/export

5. **Risques ESG**
   - Conformité environnementale
   - Pratiques sociales
   - Gouvernance et éthique

6. **Risques technologiques et cyber**
   - Sécurité informatique
   - Protection des données
   - Continuité numérique

**Évaluation et plan d'action :**
- Matrice de criticité (probabilité x impact)
- Cartographie des risques prioritaires
- Mesures de mitigation pour chaque risque
- Plan de continuité d'activité
- Indicateurs de surveillance (KRI)
- Fréquence de réévaluation recommandée""",
                "type": "internal",
                "variables": ["nom_entreprise", "secteur_activite", "niveau_risque_fournisseur", "procedures_audit", "fournisseur_principal"],
                "uses_cockpit_data": True,
                "is_system": True
            },
            {
                "id": "internal_5",
                "title": "Optimisation des Processus Achats",
                "category": "Stratégie Achats",
                "description": "Analyse et recommandations pour optimiser les processus achats de l'organisation.",
                "content": """Vous êtes un consultant expert en optimisation des processus achats. Analysez nos processus actuels et proposez des améliorations.

**Configuration actuelle :**
- Entreprise : {nom_entreprise}
- Taille : {nb_employees} employés
- Budget achats : {budget_achats_annuel}
- Système ERP : {systeme_erp}
- Outils achats : {outils_achats}

**Processus actuels :**
- Processus de validation : {processus_validation}
- Workflows d'approbation : {workflows_approbation}
- Seuils d'approbation : {seuils_approbation}
- Nombre de fournisseurs actifs : {nb_fournisseurs_actifs}

**Axes d'analyse :**

1. **Efficacité opérationnelle**
   - Temps de cycle des processus
   - Niveau d'automatisation
   - Points de friction identifiés
   - Charge de travail équipes

2. **Gouvernance et contrôle**
   - Respect des procédures
   - Séparation des tâches
   - Traçabilité des décisions
   - Gestion des exceptions

3. **Performance économique**
   - Taux de conformité budgétaire
   - Économies réalisées
   - Coût du processus achats
   - ROI des initiatives

4. **Gestion fournisseurs**
   - Rationalisation du panel
   - Évaluation et développement
   - Relations partenariales
   - Innovation collaborative

5. **Outils et digitalisation**
   - Couverture fonctionnelle
   - Intégration des systèmes
   - Automatisation possible
   - Expérience utilisateur

**Recommandations attendues :**
- Cartographie des processus optimisés
- Plan de transformation avec priorités
- Bénéfices quantifiés attendus
- Ressources et budget nécessaires
- Planning de mise en œuvre
- Indicateurs de succès (KPI)""",
                "type": "internal",
                "variables": ["nom_entreprise", "nb_employees", "budget_achats_annuel", "systeme_erp", "outils_achats", "processus_validation", "workflows_approbation", "seuils_approbation", "nb_fournisseurs_actifs"],
                "uses_cockpit_data": True,
                "is_system": True
            },
            {
                "id": "internal_6",
                "title": "Tableau de Bord Achats Personnalisé",
                "category": "Reporting et Analyse",
                "description": "Conception d'un tableau de bord achats adapté aux besoins spécifiques de l'organisation.",
                "content": """En tant qu'expert en pilotage de la performance achats, concevez un tableau de bord adapté à notre organisation.

**Profil organisation :**
- Entreprise : {nom_entreprise}
- Secteur : {secteur_activite}
- Budget achats : {budget_achats_annuel}
- KPI actuels : {kpi_achats}
- Fréquence reporting : {frequence_reporting}

**Objectifs stratégiques :**
- Objectifs réduction coûts : {objectifs_reduction_couts}
- Focus sur : [À préciser selon contexte]

**Dimensions du tableau de bord :**

1. **Performance financière**
   - Économies réalisées vs objectifs
   - Évolution des prix d'achat
   - Respect budgétaire par catégorie
   - Coût total d'acquisition (TCO)
   - ROI des initiatives achats

2. **Performance opérationnelle**
   - Taux de service fournisseurs
   - Délais de cycle des processus
   - Qualité des livraisons
   - Taux de conformité
   - Productivité équipes achats

3. **Gestion fournisseurs**
   - Nombre de fournisseurs actifs/nouveaux
   - Concentration du panel
   - Performance fournisseurs (score global)
   - Taux de renouvellement contrats
   - Satisfaction fournisseurs

4. **Risques et conformité**
   - Exposition aux risques
   - Taux d'audits réalisés
   - Non-conformités détectées
   - Couverture assurance
   - Score ESG moyen du panel

5. **Innovation et développement**
   - Projets d'innovation en cours
   - Économies process vs produit
   - Partenariats stratégiques
   - Nouvelles technologies adoptées

**Spécifications techniques :**
- Fréquence de mise à jour recommandée
- Sources de données nécessaires
- Niveaux d'accès et diffusion
- Alertes et seuils critiques
- Format de présentation (dashboard, rapport...)
- Intégration avec systèmes existants

**Plan de mise en œuvre :**
- Phases de déploiement
- Ressources nécessaires
- Formation des utilisateurs
- Planning de déploiement""",
                "type": "internal",
                "variables": ["nom_entreprise", "secteur_activite", "budget_achats_annuel", "kpi_achats", "frequence_reporting", "objectifs_reduction_couts"],
                "uses_cockpit_data": True,
                "is_system": True
            },
            {
                "id": "internal_7",
                "title": "Plan de Continuité Fournisseurs",
                "category": "Gestion des Risques",
                "description": "Élaboration d'un plan de continuité d'activité centré sur la gestion des risques fournisseurs.",
                "content": """Vous êtes un expert en continuité d'activité. Élaborez un plan de continuité spécifique à la gestion des risques fournisseurs.

**Contexte entreprise :**
- Organisation : {nom_entreprise}
- Secteur : {secteur_activite}
- Localisation : {pays_siege}, {ville_siege}
- Plan continuité existant : {plan_continuite}

**Portefeuille fournisseurs :**
- Fournisseurs actifs : {nb_fournisseurs_actifs}
- Fournisseur principal : {fournisseur_principal}
- Catégories d'achats : {categories_achats}

**Éléments du plan de continuité :**

1. **Analyse d'impact Business (BIA)**
   - Identification des fournisseurs critiques
   - Cartographie des dépendances
   - Évaluation des impacts par scénario
   - Définition des seuils de criticité

2. **Scénarios de risque**
   - Défaillance fournisseur unique
   - Perturbation géographique/sectorielle
   - Crise systémique (pandémie, conflit...)
   - Cyberattaque fournisseur critique
   - Rupture de la chaîne logistique

3. **Stratégies de mitigation**
   - Diversification des sources
   - Stocks de sécurité stratégiques
   - Contrats de backup
   - Clauses contractuelles spécifiques
   - Partenariats d'urgence

4. **Procédures d'activation**
   - Déclencheurs et seuils d'alerte
   - Escalade et prise de décision
   - Communications internes/externes
   - Activation des solutions de secours
   - Coordination avec les fournisseurs

5. **Gestion de crise**
   - Cellule de crise achats
   - Tableau de bord de suivi temps réel
   - Communication avec les parties prenantes
   - Documentation des actions
   - Retour d'expérience

**Plan de mise en œuvre :**
- Organisation et responsabilités
- Formation des équipes
- Tests et exercices de simulation
- Mise à jour et révision régulière
- Indicateurs de performance du plan

**Kit de déploiement :**
- Matrice de criticité fournisseurs
- Procédures détaillées par scénario
- Contacts d'urgence
- Modèles de communication
- Outils de suivi et reporting""",
                "type": "internal",
                "variables": ["nom_entreprise", "secteur_activite", "pays_siege", "ville_siege", "plan_continuite", "nb_fournisseurs_actifs", "fournisseur_principal", "categories_achats"],
                "uses_cockpit_data": True,
                "is_system": True
            },
            {
                "id": "internal_8",
                "title": "Analyse Concurrentielle des Fournisseurs",
                "category": "Veille Marché",
                "description": "Analyse comparative des fournisseurs et de leur positionnement concurrentiel.",
                "content": """En tant qu'expert en analyse concurrentielle, effectuez une analyse comparative de notre panel fournisseurs.

**Contexte marché :**
- Entreprise : {nom_entreprise}
- Secteur d'activité : {secteur_activite}
- Veille marché actuelle : {veille_marche}
- Benchmark concurrentiel : {benchmark_concurrentiel}

**Périmètre d'analyse :**
- Fournisseur principal : {fournisseur_principal}
- Catégories étudiées : {categories_achats}
- Tendances secteur : {tendances_secteur}

**Axes d'analyse concurrentielle :**

1. **Positionnement marché**
   - Part de marché des fournisseurs
   - Leadership technologique
   - Positionnement prix/qualité
   - Différenciation concurrentielle
   - Zones géographiques couvertes

2. **Capacités et ressources**
   - Capacités de production
   - Investissements R&D
   - Ressources humaines et expertise
   - Infrastructure et logistique
   - Solidité financière

3. **Offre et innovation**
   - Largeur et profondeur de gamme
   - Innovations récentes/à venir
   - Services associés
   - Customisation possible
   - Roadmap produits

4. **Performance client**
   - Références clients
   - Satisfaction et fidélisation
   - Service client et support
   - Réactivité et flexibilité
   - Résolution de problèmes

5. **Stratégie et évolution**
   - Orientations stratégiques
   - Acquisitions et partenariats
   - Transformation digitale
   - Expansion géographique
   - Initiatives ESG

**Grille comparative :**
- Matrice de positionnement concurrentiel
- Forces et faiblesses relatives
- Opportunités et menaces
- Recommandations de sourcing
- Stratégie de panel optimale

**Plan d'action :**
- Optimisation du panel actuel
- Identification de nouveaux fournisseurs
- Renégociation des contrats existants
- Veille concurrentielle continue
- Indicateurs de suivi marché""",
                "type": "internal",
                "variables": ["nom_entreprise", "secteur_activite", "veille_marche", "benchmark_concurrentiel", "fournisseur_principal", "categories_achats", "tendances_secteur"],
                "uses_cockpit_data": True,
                "is_system": True
            },
            {
                "id": "internal_9",
                "title": "Évaluation de Conformité Réglementaire",
                "category": "Conformité et Réglementation",
                "description": "Audit de conformité réglementaire des fournisseurs selon les exigences sectorielles.",
                "content": """Vous êtes un expert en conformité réglementaire. Conduisez un audit de conformité de nos fournisseurs.

**Cadre réglementaire :**
- Entreprise : {nom_entreprise}
- Secteur : {secteur_activite}
- Pays d'opération : {pays_siege}
- Contraintes réglementaires : {contraintes_reglementaires}
- Exigences conformité : {exigences_conformite}

**Périmètre d'audit :**
- Fournisseur évalué : {fournisseur_principal}
- Certifications qualité : {certifications_qualite}
- Évolution réglementaire : {reglementation_evolution}

**Domaines de conformité :**

1. **Réglementation sectorielle**
   - Normes spécifiques au secteur
   - Certifications obligatoires
   - Licences et autorisations
   - Standards techniques
   - Réglementations douanières

2. **Droit du travail et social**
   - Respect des conventions ILO
   - Droit du travail local
   - Santé et sécurité au travail
   - Non-discrimination
   - Travail des enfants

3. **Environnement et développement durable**
   - Réglementation environnementale
   - Gestion des déchets
   - Émissions et pollution
   - Économie circulaire
   - Reporting ESG

4. **Protection des données et cybersécurité**
   - RGPD/équivalents locaux
   - Sécurité des données
   - Transferts internationaux
   - Cyber-résilience
   - Certification sécurité

5. **Éthique et anti-corruption**
   - Lois anti-corruption
   - Code de conduite
   - Conflits d'intérêts
   - Transparence financière
   - Due diligence

6. **Qualité et sécurité produits**
   - Normes de sécurité
   - Marquage CE/équivalents
   - Traçabilité
   - Rappels produits
   - Responsabilité produits

**Grille d'évaluation :**
- Statut de conformité par domaine
- Écarts identifiés et criticité
- Risques de non-conformité
- Actions correctives requises
- Délais de mise en conformité

**Plan de suivi :**
- Programme d'audits réguliers
- Veille réglementaire
- Formation fournisseurs
- Clauses contractuelles
- Indicateurs de conformité""",
                "type": "internal",
                "variables": ["nom_entreprise", "secteur_activite", "pays_siege", "contraintes_reglementaires", "exigences_conformite", "fournisseur_principal", "certifications_qualite", "reglementation_evolution"],
                "uses_cockpit_data": True,
                "is_system": True
            },
            {
                "id": "internal_10",
                "title": "Innovation Collaborative Fournisseurs",
                "category": "Innovation et Technologie",
                "description": "Programme d'innovation collaborative avec les fournisseurs stratégiques.",
                "content": """En tant qu'expert en innovation collaborative, développez un programme d'innovation avec nos fournisseurs.

**Contexte innovation :**
- Entreprise : {nom_entreprise}
- Secteur : {secteur_activite}
- Innovations recherchées : {innovations_recherchees}
- Technologies émergentes : {technologies_emergentes}

**Écosystème actuel :**
- Fournisseur stratégique : {fournisseur_principal}
- Partenariats stratégiques : {partenariats_strategiques}
- Projets transformation : {projets_transformation}

**Structuration du programme :**

1. **Identification des opportunités**
   - Cartographie des besoins innovation
   - Analyse des gaps technologiques
   - Benchmark des meilleures pratiques
   - Veille technologique sectorielle
   - Potentiel de différenciation

2. **Sélection des partenaires**
   - Critères de sélection fournisseurs
   - Évaluation des capacités R&D
   - Complémentarité technologique
   - Appétence pour l'innovation
   - Stabilité financière et engagement

3. **Modalités de collaboration**
   - Gouvernance des projets
   - Répartition des investissements
   - Propriété intellectuelle
   - Partage des risques/bénéfices
   - Exclusivité et non-concurrence

4. **Projets d'innovation**
   - Amélioration produits existants
   - Développement nouvelles solutions
   - Optimisation des processus
   - Innovation de rupture
   - Solutions digitales

5. **Gestion du programme**
   - Instances de pilotage
   - Revues d'avancement
   - Jalons et livrables
   - Métriques de succès
   - Communication interne/externe

**Framework d'évaluation :**
- Grille d'évaluation des projets
- Critères de go/no-go
- ROI et business case
- Gestion des échecs
- Capitalisation des apprentissages

**Plan de déploiement :**
- Phase pilote avec fournisseurs sélectionnés
- Montée en charge progressive
- Formation des équipes
- Outils et processus support
- Budget et ressources allouées

**Bénéfices attendus :**
- Innovations breakthrough
- Amélioration de la compétitivité
- Renforcement des partenariats
- Accélération du time-to-market
- Création de valeur partagée""",
                "type": "internal",
                "variables": ["nom_entreprise", "secteur_activite", "innovations_recherchees", "technologies_emergentes", "fournisseur_principal", "partenariats_strategiques", "projets_transformation"],
                "uses_cockpit_data": True,
                "is_system": True
            }
        ],
        "external_prompts": [
            {
                "id": "external_1",
                "title": "Benchmark Tarifaire Sectoriel",
                "category": "Veille Marché",
                "description": "Analyse comparative des tarifs pratiqués dans le secteur avec recommandations de négociation.",
                "content": "<p>Vous êtes un expert en analyse de marché spécialisé dans le secteur <strong>[SECTEUR D'ACTIVITÉ]</strong>. Je souhaite réaliser un benchmark tarifaire pour optimiser mes négociations fournisseurs.</p><p><strong>Contexte :</strong></p><ul><li>Entreprise : [NOM ENTREPRISE]</li><li>Secteur d'activité : [SECTEUR]</li><li>Volume d'achats annuel : [BUDGET]</li><li>Géographie : [PAYS/RÉGION]</li></ul><p><strong>Catégories d'achats à analyser :</strong></p><ul><li>[CATÉGORIE 1] - Volume annuel : [MONTANT]</li><li>[CATÉGORIE 2] - Volume annuel : [MONTANT]</li><li>[CATÉGORIE 3] - Volume annuel : [MONTANT]</li></ul><p><strong>Analyse attendue :</strong></p><ol><li><strong>Tendances tarifaires du marché</strong><ul><li>Évolution des prix sur 12-24 mois</li><li>Facteurs d'influence (matières premières, réglementation, etc.)</li><li>Saisonnalité et cycles</li></ul></li><li><strong>Positionnement concurrentiel</strong><ul><li>Fourchettes de prix par catégorie</li><li>Positionnement de nos fournisseurs actuels</li><li>Opportunités d'économies identifiées</li></ul></li><li><strong>Stratégie de négociation</strong><ul><li>Arguments de négociation par catégorie</li><li>Timing optimal pour les renégociations</li><li>Leviers de pression disponibles</li></ul></li><li><strong>Recommandations actionables</strong><ul><li>Objectifs d'économies réalistes</li><li>Plan d'action par fournisseur</li><li>Alternatives à considérer</li></ul></li></ol>",
                "type": "external",
                "variables": [],
                "uses_cockpit_data": False,
                "is_system": True
            },
            {
                "id": "external_2",
                "title": "Cahier des Charges Appel d'Offres",
                "category": "Stratégie Achats",
                "description": "Rédaction complète d'un cahier des charges pour appel d'offres structuré et professionnel.",
                "content": "<p>Vous êtes un expert en rédaction de cahiers des charges et appels d'offres. Rédigez un cahier des charges complet et structuré pour notre appel d'offres.</p><p><strong>Informations générales :</strong></p><ul><li>Entreprise : [NOM ENTREPRISE]</li><li>Secteur : [SECTEUR D'ACTIVITÉ]</li><li>Objet de l'appel d'offres : [DESCRIPTION DÉTAILLÉE]</li><li>Budget estimé : [MONTANT]</li><li>Calendrier souhaité : [PLANNING]</li></ul><p><strong>Structure du cahier des charges :</strong></p><ol><li><strong>Présentation de l'entreprise et du projet</strong><ul><li>Contexte et enjeux</li><li>Objectifs du projet</li><li>Périmètre et contraintes</li></ul></li><li><strong>Spécifications techniques détaillées</strong><ul><li>Exigences fonctionnelles</li><li>Exigences techniques</li><li>Normes et standards applicables</li><li>Contraintes d'intégration</li></ul></li><li><strong>Exigences qualité et performance</strong><ul><li>Niveaux de service attendus</li><li>Indicateurs de performance (KPI)</li><li>Processus de contrôle qualité</li><li>Pénalités en cas de non-respect</li></ul></li><li><strong>Modalités contractuelles</strong><ul><li>Type de contrat souhaité</li><li>Durée et renouvellement</li><li>Conditions de paiement</li><li>Clauses spécifiques (confidentialité, propriété intellectuelle)</li></ul></li><li><strong>Critères d'évaluation des offres</strong><ul><li>Grille de notation détaillée</li><li>Pondération des critères</li><li>Processus de sélection</li><li>Documentation à fournir</li></ul></li><li><strong>Modalités de réponse</strong><ul><li>Format et structure de la réponse</li><li>Documents à joindre</li><li>Calendrier de l'appel d'offres</li><li>Contacts et modalités de questions</li></ul></li></ol><p><strong>Annexes à prévoir :</strong></p><ul><li>Grille de réponse standardisée</li><li>Modèle de planning projet</li><li>Exemples ou références</li><li>Conditions générales d'achat</li></ul>",
                "type": "external",
                "variables": [],
                "uses_cockpit_data": False,
                "is_system": True
            },
            {
                "id": "external_3",
                "title": "Politique Achats Responsables",
                "category": "RSE et Développement Durable",
                "description": "Élaboration d'une politique d'achats responsables intégrant les enjeux ESG.",
                "content": "<p>En tant qu'expert en achats responsables et développement durable, rédigez une politique d'achats responsables complète pour notre organisation.</p><p><strong>Contexte organisation :</strong></p><ul><li>Entreprise : [NOM ENTREPRISE]</li><li>Secteur : [SECTEUR D'ACTIVITÉ]</li><li>Taille : [NOMBRE D'EMPLOYÉS] employés</li><li>Implantations : [GÉOGRAPHIE]</li><li>Budget achats annuel : [MONTANT]</li></ul><p><strong>Enjeux RSE prioritaires :</strong></p><ul><li>Environnement : [OBJECTIFS ENVIRONNEMENTAUX]</li><li>Social : [OBJECTIFS SOCIAUX]</li><li>Gouvernance : [OBJECTIFS GOUVERNANCE]</li><li>Certifications visées : [CERTIFICATIONS]</li></ul><p><strong>Structure de la politique :</strong></p><ol><li><strong>Vision et engagements</strong><ul><li>Déclaration d'intention du dirigeant</li><li>Valeurs et principes fondamentaux</li><li>Objectifs stratégiques RSE</li><li>Alignement avec les ODD</li></ul></li><li><strong>Périmètre et gouvernance</strong><ul><li>Scope d'application</li><li>Rôles et responsabilités</li><li>Instances de pilotage</li><li>Processus de décision</li></ul></li><li><strong>Critères et exigences fournisseurs</strong><ul><li>Critères environnementaux obligatoires</li><li>Exigences sociales et éthiques</li><li>Standards de gouvernance</li><li>Certifications requises</li></ul></li><li><strong>Processus d'évaluation et sélection</strong><ul><li>Grille d'évaluation ESG</li><li>Processus de due diligence</li><li>Critères d'exclusion</li><li>Pondération RSE dans les appels d'offres</li></ul></li><li><strong>Accompagnement et développement</strong><ul><li>Programme de développement fournisseurs</li><li>Formations et sensibilisation</li><li>Partage de bonnes pratiques</li><li>Innovation collaborative durable</li></ul></li><li><strong>Suivi et reporting</strong><ul><li>Indicateurs de performance RSE</li><li>Audits et contrôles</li><li>Reporting externe</li><li>Communication et transparence</li></ul></li></ol><p><strong>Plan de déploiement :</strong></p><ul><li>Phase pilote et généralisation</li><li>Formation des équipes</li><li>Communication interne et externe</li><li>Budget et ressources</li><li>Planning de mise en œuvre</li></ul>",
                "type": "external",
                "variables": [],
                "uses_cockpit_data": False,
                "is_system": True
            },
            {
                "id": "external_4",
                "title": "Matrice d'Évaluation Fournisseurs",
                "category": "Évaluation Fournisseur",
                "description": "Création d'une matrice d'évaluation fournisseurs multi-critères avec système de notation.",
                "content": "<p>Vous êtes un expert en évaluation et gestion de la performance fournisseurs. Concevez une matrice d'évaluation complète et opérationnelle.</p><p><strong>Contexte évaluation :</strong></p><ul><li>Entreprise : [NOM ENTREPRISE]</li><li>Secteur : [SECTEUR D'ACTIVITÉ]</li><li>Types de fournisseurs : [CATÉGORIES]</li><li>Fréquence d'évaluation : [ANNUELLE/SEMESTRIELLE]</li><li>Nombre de fournisseurs à évaluer : [NOMBRE]</li></ul><p><strong>Objectifs de l'évaluation :</strong></p><ul><li>Mesurer la performance globale</li><li>Identifier les axes d'amélioration</li><li>Segmenter le panel fournisseurs</li><li>Orienter les décisions de renouvellement</li><li>Développer les partenariats stratégiques</li></ul><p><strong>Critères d'évaluation :</strong></p><ol><li><strong>Qualité (pondération : 30%)</strong><ul><li>Conformité des produits/services</li><li>Taux de défauts et réclamations</li><li>Certifications qualité</li><li>Amélioration continue</li></ul></li><li><strong>Livraison (pondération : 25%)</strong><ul><li>Respect des délais</li><li>Fiabilité des livraisons</li><li>Flexibilité et réactivité</li><li>Gestion des urgences</li></ul></li><li><strong>Prix et conditions (pondération : 20%)</strong><ul><li>Compétitivité tarifaire</li><li>Évolution des prix</li><li>Conditions de paiement</li><li>Transparence tarifaire</li></ul></li><li><strong>Service et relation (pondération : 15%)</strong><ul><li>Qualité du service client</li><li>Réactivité aux demandes</li><li>Communication proactive</li><li>Résolution de problèmes</li></ul></li><li><strong>Innovation et développement (pondération : 10%)</strong><ul><li>Capacité d'innovation</li><li>Propositions d'amélioration</li><li>Veille technologique</li><li>Partenariat R&D</li></ul></li></ol><p><strong>Système de notation :</strong></p><ul><li>Échelle de notation (1 à 5 ou 1 à 10)</li><li>Définition de chaque niveau</li><li>Calcul du score global pondéré</li><li>Seuils de performance (excellent/bon/acceptable/insuffisant)</li></ul><p><strong>Processus d'évaluation :</strong></p><ul><li>Collecte des données (KPI, enquêtes, audits)</li><li>Grille de saisie standardisée</li><li>Validation et consolidation</li><li>Restitution aux fournisseurs</li><li>Plans d'action et suivi</li></ul><p><strong>Actions par niveau de performance :</strong></p><ul><li>Fournisseurs stratégiques (score >8/10)</li><li>Fournisseurs performants (score 6-8/10)</li><li>Fournisseurs à développer (score 4-6/10)</li><li>Fournisseurs à risque (score <4/10)</li></ul>",
                "type": "external",
                "variables": [],
                "uses_cockpit_data": False,
                "is_system": True
            },
            {
                "id": "external_5",
                "title": "Contrat de Partenariat Stratégique",
                "category": "Analyse Contractuelle",
                "description": "Modèle de contrat de partenariat stratégique avec clauses spécifiques à la relation privilégiée.",
                "content": "<p>Vous êtes un expert juridique spécialisé en droit des contrats commerciaux. Rédigez un modèle de contrat de partenariat stratégique complet.</p><p><strong>Contexte du partenariat :</strong></p><ul><li>Entreprise cliente : [NOM ENTREPRISE]</li><li>Partenaire fournisseur : [NOM FOURNISSEUR]</li><li>Objet du partenariat : [DESCRIPTION]</li><li>Durée envisagée : [DURÉE]</li><li>Montant annuel estimé : [MONTANT]</li></ul><p><strong>Spécificités du partenariat :</strong></p><ul><li>Innovation collaborative</li><li>Exclusivité partielle ou totale</li><li>Investissements mutuels</li><li>Partage de données</li><li>Objectifs de performance communs</li></ul><p><strong>Structure contractuelle :</strong></p><ol><li><strong>Préambule et définitions</strong><ul><li>Contexte et enjeux du partenariat</li><li>Définitions des termes techniques</li><li>Références aux documents annexes</li></ul></li><li><strong>Objet et périmètre</strong><ul><li>Description détaillée des prestations</li><li>Exclusivité et territorialité</li><li>Évolutions et extensions possibles</li></ul></li><li><strong>Conditions financières</strong><ul><li>Pricing et mécanismes tarifaires</li><li>Modalités de facturation</li><li>Conditions de paiement</li><li>Mécanismes d'intéressement</li></ul></li><li><strong>Gouvernance du partenariat</strong><ul><li>Instances de pilotage</li><li>Comités techniques et stratégiques</li><li>Processus de décision</li><li>Reporting et communication</li></ul></li><li><strong>Innovation et propriété intellectuelle</strong><ul><li>Projets d'innovation communs</li><li>Répartition des investissements R&D</li><li>Propriété des développements</li><li>Licences et exploitation</li></ul></li><li><strong>Niveau de service et performance</strong><ul><li>SLA (Service Level Agreements)</li><li>KPI et tableaux de bord</li><li>Processus d'amélioration continue</li><li>Pénalités et bonus</li></ul></li><li><strong>Gestion des risques</strong><ul><li>Identification et partage des risques</li><li>Assurances et garanties</li><li>Plan de continuité d'activité</li><li>Force majeure</li></ul></li><li><strong>Confidentialité et données</strong><ul><li>Engagements de confidentialité</li><li>Protection des données</li><li>Sécurité informatique</li><li>Transferts internationaux</li></ul></li><li><strong>Résiliation et fin de contrat</strong><ul><li>Conditions de résiliation</li><li>Préavis et procédures</li><li>Transfert d'activités</li><li>Obligations post-contractuelles</li></ul></li></ol><p><strong>Annexes spécialisées :</strong></p><ul><li>Spécifications techniques détaillées</li><li>Conditions générales d'achat adaptées</li><li>Grilles tarifaires et indexation</li><li>Processus de gouvernance</li><li>Plans de développement communs</li></ul>",
                "type": "external",
                "variables": [],
                "uses_cockpit_data": False,
                "is_system": True
            },
            {
                "id": "external_6",
                "title": "Plan de Transformation Digitale Achats",
                "category": "Innovation et Technologie",
                "description": "Stratégie complète de transformation digitale de la fonction achats avec roadmap technologique.",
                "content": "<p>Vous êtes un expert en transformation digitale spécialisé dans la fonction achats. Élaborez un plan de transformation digitale complet pour moderniser nos processus achats.</p><p><strong>État des lieux actuel :</strong></p><ul><li>Entreprise : [NOM ENTREPRISE]</li><li>Secteur : [SECTEUR D'ACTIVITÉ]</li><li>Budget achats annuel : [MONTANT]</li><li>Équipes achats : [NOMBRE] personnes</li><li>Systèmes actuels : [ERP/OUTILS EXISTANTS]</li><li>Niveau de maturité digitale : [DÉBUTANT/INTERMÉDIAIRE/AVANCÉ]</li></ul><p><strong>Objectifs de transformation :</strong></p><ul><li>Automatisation des processus répétitifs</li><li>Amélioration de l'expérience utilisateur</li><li>Renforcement de l'analytics et du pilotage</li><li>Optimisation de la gestion fournisseurs</li><li>Réduction des coûts opérationnels</li></ul><p><strong>Axes de transformation :</strong></p><ol><li><strong>Digitalisation des processus core</strong><ul><li>e-Procurement et catalogues électroniques</li><li>Workflows d'approbation digitaux</li><li>Signature électronique</li><li>Dématérialisation des factures</li></ul></li><li><strong>Intelligence artificielle et automatisation</strong><ul><li>Analyse prédictive des besoins</li><li>Classification automatique des dépenses</li><li>Détection d'anomalies</li><li>Chatbots pour support utilisateurs</li></ul></li><li><strong>Analytics et Business Intelligence</strong><ul><li>Tableaux de bord temps réel</li><li>Analyse des performances fournisseurs</li><li>Optimisation du sourcing</li><li>Predictive analytics</li></ul></li><li><strong>Collaboration et écosystème</strong><ul><li>Portail fournisseurs intégré</li><li>Marketplaces et plateformes</li><li>Collaboration en temps réel</li><li>APIs et intégrations</li></ul></li><li><strong>Mobilité et expérience utilisateur</strong><ul><li>Applications mobiles</li><li>Interface utilisateur moderne</li><li>Self-service étendu</li><li>Personnalisation des interfaces</li></ul></li></ol><p><strong>Roadmap de déploiement :</strong></p><ul><li><strong>Phase 1 (0-6 mois) :</strong> Fondations<ul><li>Audit et cartographie existant</li><li>Sélection des solutions</li><li>Mise en place des bases</li></ul></li><li><strong>Phase 2 (6-12 mois) :</strong> Processus core<ul><li>Déploiement e-procurement</li><li>Automatisation workflows</li><li>Formation utilisateurs</li></ul></li><li><strong>Phase 3 (12-18 mois) :</strong> Intelligence et analytics<ul><li>Mise en place BI</li><li>Déploiement IA</li><li>Optimisation processus</li></ul></li><li><strong>Phase 4 (18-24 mois) :</strong> Écosystème étendu<ul><li>Intégration fournisseurs</li><li>APIs et connecteurs</li><li>Innovation continue</li></ul></li></ul><p><strong>Facteurs clés de succès :</strong></p><ul><li>Sponsor exécutif fort</li><li>Conduite du changement structurée</li><li>Formation et accompagnement</li><li>Communication continue</li><li>Mesure ROI et bénéfices</li></ul><p><strong>Budget et ressources :</strong></p><ul><li>Estimation investissements par phase</li><li>Ressources humaines nécessaires</li><li>Coûts de formation</li><li>ROI attendu et délais</li></ul>",
                "type": "external",
                "variables": [],
                "uses_cockpit_data": False,
                "is_system": True
            },
            {
                "id": "external_7",
                "title": "Audit de Sécurité Fournisseurs",
                "category": "Gestion des Risques",
                "description": "Méthodologie d'audit de sécurité informatique et physique des fournisseurs critiques.",
                "content": "<p>Vous êtes un expert en sécurité et gestion des risques. Élaborez une méthodologie d'audit de sécurité complète pour nos fournisseurs critiques.</p><p><strong>Contexte sécuritaire :</strong></p><ul><li>Entreprise : [NOM ENTREPRISE]</li><li>Secteur : [SECTEUR D'ACTIVITÉ]</li><li>Criticité des données : [NIVEAU]</li><li>Réglementations applicables : [RGPD, ISO27001, etc.]</li><li>Incidents passés : [HISTORIQUE]</li></ul><p><strong>Périmètre de l'audit :</strong></p><ul><li>Fournisseurs critiques IT</li><li>Sous-traitants avec accès aux données</li><li>Partenaires avec connexions systèmes</li><li>Prestataires sur site</li></ul><p><strong>Domaines d'audit sécurité :</strong></p><ol><li><strong>Gouvernance et organisation sécurité</strong><ul><li>Politique de sécurité</li><li>Organisation de la sécurité</li><li>Gestion des risques</li><li>Conformité réglementaire</li><li>Sensibilisation et formation</li></ul></li><li><strong>Sécurité physique et environnementale</strong><ul><li>Contrôle d'accès physique</li><li>Protection des équipements</li><li>Sécurité des datacenters</li><li>Gestion des supports</li><li>Plan de continuité</li></ul></li><li><strong>Sécurité des systèmes d'information</strong><ul><li>Architecture de sécurité</li><li>Gestion des accès et identités</li><li>Chiffrement et cryptographie</li><li>Surveillance et détection</li><li>Gestion des vulnérabilités</li></ul></li><li><strong>Sécurité réseau et communications</strong><ul><li>Segmentation réseau</li><li>Firewall et filtrage</li><li>Sécurité des communications</li><li>VPN et accès distants</li><li>Surveillance du trafic</li></ul></li><li><strong>Développement et maintenance sécurisés</strong><ul><li>Cycle de développement sécurisé</li><li>Tests de sécurité</li><li>Gestion des changements</li><li>Maintenance préventive</li><li>Sauvegarde et restauration</li></ul></li><li><strong>Gestion des incidents de sécurité</strong><ul><li>Processus de gestion des incidents</li><li>Détection et signalement</li><li>Réponse et investigation</li><li>Communication de crise</li><li>Retour d'expérience</li></ul></li><li><strong>Protection des données personnelles</strong><ul><li>Conformité RGPD</li><li>Collecte et traitement</li><li>Droits des personnes</li><li>Transferts internationaux</li><li>DPO et gouvernance</li></ul></li></ol><p><strong>Méthodologie d'audit :</strong></p><ul><li><strong>Préparation :</strong> Questionnaire préalable, planification</li><li><strong>Audit documentaire :</strong> Revue des politiques et procédures</li><li><strong>Audit technique :</strong> Tests d'intrusion, scan de vulnérabilités</li><li><strong>Audit organisationnel :</strong> Entretiens, observation</li><li><strong>Synthèse :</strong> Rapport d'audit et plan d'action</li></ul><p><strong>Grille d'évaluation :</strong></p><ul><li>Échelle de notation par domaine</li><li>Criticité des non-conformités</li><li>Score global de sécurité</li><li>Seuils d'acceptabilité</li><li>Actions correctives obligatoires</li></ul><p><strong>Suivi et contrôle :</strong></p><ul><li>Plan d'action correctif</li><li>Échéances de mise en conformité</li><li>Audits de suivi</li><li>Pénalités contractuelles</li><li>Résiliation en cas de manquements graves</li></ul>",
                "type": "external",
                "variables": [],
                "uses_cockpit_data": False,
                "is_system": True
            },
            {
                "id": "external_8",
                "title": "Optimisation Coûts et Total Cost of Ownership",
                "category": "Stratégie Achats",
                "description": "Analyse TCO complète avec identification des leviers d'optimisation des coûts.",
                "content": "<p>Vous êtes un expert en optimisation des coûts et analyse TCO (Total Cost of Ownership). Réalisez une analyse complète pour optimiser nos coûts d'achat.</p><p><strong>Contexte économique :</strong></p><ul><li>Entreprise : [NOM ENTREPRISE]</li><li>Secteur : [SECTEUR D'ACTIVITÉ]</li><li>Budget achats total : [MONTANT ANNUEL]</li><li>Objectif d'économies : [POURCENTAGE/MONTANT]</li><li>Horizon temporel : [DURÉE]</li></ul><p><strong>Périmètre d'analyse :</strong></p><ul><li>Catégorie d'achats : [CATÉGORIE PRINCIPALE]</li><li>Fournisseurs principaux : [NOMS]</li><li>Volume annuel : [QUANTITÉS/MONTANTS]</li><li>Contrats actuels : [DURÉES ET CONDITIONS]</li></ul><p><strong>Analyse du Total Cost of Ownership :</strong></p><ol><li><strong>Coûts d'acquisition directs</strong><ul><li>Prix d'achat unitaire</li><li>Frais de transport et logistique</li><li>Assurances et douanes</li><li>Frais de mise en service</li></ul></li><li><strong>Coûts d'exploitation</strong><ul><li>Consommations (énergie, consommables)</li><li>Maintenance préventive et curative</li><li>Formation et accompagnement</li><li>Coûts de non-qualité</li></ul></li><li><strong>Coûts de fin de vie</strong><ul><li>Démantèlement et désinscription</li><li>Recyclage et traitement</li><li>Remise en état</li><li>Obsolescence</li></ul></li><li><strong>Coûts cachés et indirects</strong><ul><li>Temps de gestion interne</li><li>Coûts de stockage</li><li>Risques et assurances</li><li>Coût du capital immobilisé</li></ul></li></ol><p><strong>Leviers d'optimisation identifiés :</strong></p><ol><li><strong>Optimisation du sourcing</strong><ul><li>Élargissement du panel fournisseurs</li><li>Négociation groupée/consortiums</li><li>Optimisation géographique</li><li>Contrats long terme vs spot</li></ul></li><li><strong>Rationalisation des besoins</strong><ul><li>Standardisation des spécifications</li><li>Mutualisation des achats</li><li>Optimisation des volumes</li><li>Révision des cahiers des charges</li></ul></li><li><strong>Innovation dans l'approche</strong><ul><li>Nouvelles technologies alternatives</li><li>Économie de fonctionnalité</li><li>Partenariats innovants</li><li>Solutions de substitution</li></ul></li><li><strong>Amélioration des processus</strong><ul><li>Automatisation des tâches</li><li>Réduction des délais</li><li>Diminution des rebuts</li><li>Optimisation logistique</li></ul></li></ol><p><strong>Plan d'action chiffré :</strong></p><ul><li><strong>Actions court terme (0-6 mois) :</strong><ul><li>Renégociations prioritaires</li><li>Quick wins identifiés</li><li>Économies attendues : [MONTANT]</li></ul></li><li><strong>Actions moyen terme (6-18 mois) :</strong><ul><li>Projets de rationalisation</li><li>Nouveaux sourcing</li><li>Économies attendues : [MONTANT]</li></ul></li><li><strong>Actions long terme (18+ mois) :</strong><ul><li>Transformation structurelle</li><li>Innovation et partenariats</li><li>Économies attendues : [MONTANT]</li></ul></li></ul><p><strong>Suivi et mesure :</strong></p><ul><li>KPI de suivi des économies</li><li>Tableau de bord TCO</li><li>Reporting mensuel/trimestriel</li><li>Révision annuelle de la stratégie</li></ul>",
                "type": "external",
                "variables": [],
                "uses_cockpit_data": False,
                "is_system": True
            },
            {
                "id": "external_9",
                "title": "Stratégie de Diversification Fournisseurs",
                "category": "Gestion des Risques",
                "description": "Plan de diversification du panel fournisseurs pour réduire les risques de dépendance.",
                "content": "<p>Vous êtes un expert en gestion des risques fournisseurs et diversification du sourcing. Élaborez une stratégie de diversification pour sécuriser notre chaîne d'approvisionnement.</p><p><strong>Situation actuelle :</strong></p><ul><li>Entreprise : [NOM ENTREPRISE]</li><li>Secteur : [SECTEUR D'ACTIVITÉ]</li><li>Nombre de fournisseurs actifs : [NOMBRE]</li><li>Fournisseurs représentant 80% des achats : [NOMBRE]</li><li>Concentration géographique : [PAYS/RÉGIONS]</li></ul><p><strong>Risques identifiés :</strong></p><ul><li>Sur-dépendance à certains fournisseurs critiques</li><li>Concentration géographique excessive</li><li>Vulnérabilité aux crises sectorielles</li><li>Manque d'alternatives crédibles</li><li>Pouvoir de négociation déséquilibré</li></ul><p><strong>Analyse de la concentration actuelle :</strong></p><ol><li><strong>Analyse par fournisseur</strong><ul><li>Top 10 des fournisseurs (% CA)</li><li>Dépendance mutuelle</li><li>Criticité pour l'activité</li><li>Facilité de substitution</li></ul></li><li><strong>Analyse par catégorie</strong><ul><li>Répartition par famille d'achats</li><li>Nombre de fournisseurs par catégorie</li><li>Indices de concentration</li><li>Barrières à l'entrée</li></ul></li><li><strong>Analyse géographique</strong><ul><li>Répartition par pays/régions</li><li>Risques géopolitiques</li><li>Risques logistiques</li><li>Diversité des écosystèmes</li></ul></li></ol><p><strong>Stratégie de diversification :</strong></p><ol><li><strong>Identification de nouveaux fournisseurs</strong><ul><li>Cartographie mondiale des capacités</li><li>Sourcing dans de nouveaux pays/régions</li><li>Qualification de fournisseurs alternatifs</li><li>Développement de fournisseurs émergents</li></ul></li><li><strong>Segmentation et priorisation</strong><ul><li>Matrice criticité/substitution</li><li>Priorisation des actions par risque</li><li>Approche différenciée par catégorie</li><li>Planning de déploiement</li></ul></li><li><strong>Modèles de sourcing adaptés</strong><ul><li>Multi-sourcing vs single sourcing</li><li>Fournisseurs principaux/secondaires</li><li>Contrats contingents</li><li>Accords de backup</li></ul></li><li><strong>Développement d'écosystèmes</strong><ul><li>Partenariats régionaux</li><li>Soutien aux PME locales</li><li>Investissements dans les capacités</li><li>Innovation collaborative</li></ul></li></ol><p><strong>Plan d'action opérationnel :</strong></p><ul><li><strong>Phase 1 - Diagnostic et priorisation</strong><ul><li>Audit du panel actuel</li><li>Cartographie des risques</li><li>Définition des objectifs</li></ul></li><li><strong>Phase 2 - Sourcing et qualification</strong><ul><li>Recherche de nouveaux fournisseurs</li><li>Processus de qualification</li><li>Tests et validation</li></ul></li><li><strong>Phase 3 - Intégration progressive</strong><ul><li>Attribution de volumes tests</li><li>Montée en charge contrôlée</li><li>Développement des capacités</li></ul></li><li><strong>Phase 4 - Optimisation continue</strong><ul><li>Révision régulière du panel</li><li>Ajustement des volumes</li><li>Performance monitoring</li></ul></li></ul><p><strong>Critères de réussite :</strong></p><ul><li>Réduction de la concentration (indice HHI)</li><li>Amélioration de la résilience</li><li>Maintien de la qualité</li><li>Maîtrise des coûts</li><li>Délais de substitution raccourcis</li></ul><p><strong>Gouvernance et suivi :</strong></p><ul><li>Comité de pilotage diversification</li><li>Indicateurs de suivi mensuel</li><li>Revue trimestrielle des risques</li><li>Tests de continuité réguliers</li></ul>",
                "type": "external",
                "variables": [],
                "uses_cockpit_data": False,
                "is_system": True
            },
            {
                "id": "external_10",
                "title": "Programme de Développement Durable",
                "category": "RSE et Développement Durable",
                "description": "Conception d'un programme complet d'achats durables avec objectifs ESG mesurables.",
                "content": "<p>Vous êtes un expert en développement durable et achats responsables. Concevez un programme complet d'achats durables aligné sur les objectifs ESG de notre organisation.</p><p><strong>Contexte ESG :</strong></p><ul><li>Entreprise : [NOM ENTREPRISE]</li><li>Secteur : [SECTEUR D'ACTIVITÉ]</li><li>Engagement climatique : [OBJECTIFS CARBONE]</li><li>Certifications visées : [B-CORP, ISO14001, etc.]</li><li>Reporting ESG : [STANDARDS SUIVIS]</li></ul><p><strong>Enjeux prioritaires :</strong></p><ul><li>Réduction empreinte carbone</li><li>Économie circulaire</li><li>Éthique et droits humains</li><li>Innovation durable</li><li>Impact local et social</li></ul><p><strong>Programme d'achats durables :</strong></p><ol><li><strong>Gouvernance et pilotage ESG</strong><ul><li>Comité de pilotage ESG achats</li><li>Référent développement durable</li><li>Formation équipes achats</li><li>Intégration dans les processus</li></ul></li><li><strong>Évaluation et sélection durable</strong><ul><li>Critères ESG dans les appels d'offres</li><li>Questionnaires de qualification ESG</li><li>Audit et certification fournisseurs</li><li>Score de durabilité global</li></ul></li><li><strong>Objectifs environnementaux</strong><ul><li>Réduction émissions scope 3</li><li>Approvisionnement énergies renouvelables</li><li>Économie circulaire et recyclage</li><li>Réduction déchets et emballages</li><li>Préservation biodiversité</li></ul></li><li><strong>Dimension sociale et éthique</strong><ul><li>Respect droits humains fondamentaux</li><li>Conditions de travail décentes</li><li>Égalité et non-discrimination</li><li>Développement communautés locales</li><li>Chaîne d'approvisionnement éthique</li></ul></li><li><strong>Innovation et économie circulaire</strong><ul><li>Éco-conception des produits</li><li>Solutions de réemploi/réparation</li><li>Partenariats innovation durable</li><li>Technologies vertes</li><li>Modèles économiques circulaires</li></ul></li><li><strong>Sourcing local et responsable</strong><ul><li>Privilégier les circuits courts</li><li>Soutien aux PME locales</li><li>Commerce équitable</li><li>Agriculture raisonnée/bio</li><li>Secteur adapté et inclusif</li></ul></li></ol><p><strong>Plan d'action par phase :</strong></p><ul><li><strong>Phase 1 (0-12 mois) - Fondations</strong><ul><li>Diagnostic ESG du panel actuel</li><li>Formation équipes et sensibilisation</li><li>Intégration critères ESG dans processus</li><li>Premiers contrats pilotes</li></ul></li><li><strong>Phase 2 (12-24 mois) - Déploiement</strong><ul><li>Généralisation critères ESG</li><li>Programme développement fournisseurs</li><li>Partenariats innovation durable</li><li>Mesure et reporting impacts</li></ul></li><li><strong>Phase 3 (24+ mois) - Excellence</strong><ul><li>Leadership sectoriel</li><li>Écosystème durable mature</li><li>Innovation collaborative</li><li>Certification et reconnaissance</li></ul></li></ul><p><strong>Indicateurs de performance :</strong></p><ul><li><strong>Environnement :</strong><ul><li>% réduction émissions CO2 scope 3</li><li>% achats éco-labellisés</li><li>Taux recyclage/réemploi</li><li>% énergies renouvelables</li></ul></li><li><strong>Social :</strong><ul><li>% fournisseurs audités droits humains</li><li>Score diversité du panel</li><li>% achats solidaires/locaux</li><li>Emplois créés/maintenus</li></ul></li><li><strong>Gouvernance :</strong><ul><li>% fournisseurs certifiés ESG</li><li>Score transparence chaîne</li><li>Taux conformité code conduite</li><li>% objectifs ESG atteints</li></ul></li></ul><p><strong>Communication et reporting :</strong></p><ul><li>Rapport annuel développement durable</li><li>Communication interne/externe</li><li>Participation initiatives sectorielles</li><li>Benchmarking et bonnes pratiques</li></ul>",
                "type": "external",
                "variables": [],
                "uses_cockpit_data": False,
                "is_system": True
            }
        ]
    }
    
    # Chemins des fichiers
    data_dir = Path('data')
    prompts_file = data_dir / 'prompts.json'
    
    # Charger les prompts existants
    if prompts_file.exists():
        with open(prompts_file, 'r', encoding='utf-8') as f:
            existing_prompts = json.load(f)
    else:
        existing_prompts = {"system_prompts": []}
    
    # Ajouter les nouveaux prompts
    if "system_prompts" not in existing_prompts:
        existing_prompts["system_prompts"] = []
    
    # Ajouter les prompts internes
    for prompt in new_prompts["internal_prompts"]:
        existing_prompts["system_prompts"].append(prompt)
    
    # Ajouter les prompts externes  
    for prompt in new_prompts["external_prompts"]:
        existing_prompts["system_prompts"].append(prompt)
    
    # Sauvegarder le fichier mis à jour
    with open(prompts_file, 'w', encoding='utf-8') as f:
        json.dump(existing_prompts, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {len(new_prompts['internal_prompts']) + len(new_prompts['external_prompts'])} nouveaux prompts importés avec succès!")
    
    return existing_prompts

if __name__ == "__main__":
    import_new_prompts()