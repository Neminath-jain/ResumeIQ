from django.test import TestCase
from resume_analyzer.services.rag_skill_matcher import match_skills_rag


class RAGSkillMatcherTestCase(TestCase):

    def test_exact_skill_matches(self):
        resume_skills = ["Python", "Django", "PostgreSQL"]
        required_skills = ["Python", "Django"]

        result = match_skills_rag(resume_skills, required_skills)

        self.assertEqual(len(result["exact_matches"]), 2)
        self.assertEqual(len(result["still_missing_skills"]), 0)
        self.assertEqual(result["semantic_score"], 100.0)

    def test_semantic_skill_matches_above_threshold(self):
        resume_skills = ["Postgres", "React", "ML"]
        required_skills = ["PostgreSQL", "Machine Learning"]

        result = match_skills_rag(resume_skills, required_skills, similarity_threshold=0.75)

        total_matched = len(result["exact_matches"]) + len(result["semantic_matches"])
        self.assertEqual(total_matched, 2)
        self.assertEqual(len(result["still_missing_skills"]), 0)
        self.assertGreaterEqual(result["semantic_score"], 80.0)

    def test_missing_skills_below_threshold(self):
        resume_skills = ["Python", "HTML"]
        required_skills = ["Python", "Kubernetes", "AWS Cloud"]

        result = match_skills_rag(resume_skills, required_skills, similarity_threshold=0.75)

        self.assertEqual(len(result["exact_matches"]), 1)
        self.assertIn("Kubernetes", result["still_missing_skills"])
        self.assertIn("AWS Cloud", result["still_missing_skills"])

    def test_empty_skills_edge_cases(self):
        # Empty JD required skills
        result_empty_jd = match_skills_rag(["Python"], [])
        self.assertEqual(result_empty_jd["semantic_score"], 50.0)
        self.assertEqual(result_empty_jd["total_required"], 0)

        # Empty resume skills
        result_empty_resume = match_skills_rag([], ["Python", "Django"])
        self.assertEqual(result_empty_resume["semantic_score"], 0.0)
        self.assertEqual(len(result_empty_resume["still_missing_skills"]), 2)

    def test_compound_and_parenthesized_skills(self):
        from resume_analyzer.services.rag_skill_matcher import check_exact_or_alias
        # Parenthesized sub-skill matching
        self.assertTrue(check_exact_or_alias("SQL (PostgreSQL, MySQL)", "PostgreSQL"))
        self.assertTrue(check_exact_or_alias("SQL (PostgreSQL, MySQL)", "SQL"))
        self.assertTrue(check_exact_or_alias("TensorFlow or PyTorch", "PyTorch"))
        self.assertTrue(check_exact_or_alias("Docker / Kubernetes", "Docker"))

    def test_tech_alias_expansions(self):
        from resume_analyzer.services.rag_skill_matcher import check_exact_or_alias
        self.assertTrue(check_exact_or_alias("React.js", "React"))
        self.assertTrue(check_exact_or_alias("NodeJS", "Node.js"))
        self.assertTrue(check_exact_or_alias("Golang", "Go"))
        self.assertTrue(check_exact_or_alias("AWS", "Amazon Web Services"))
        self.assertTrue(check_exact_or_alias("CI/CD", "Continuous Integration"))

    def test_rule_based_fallback_extractor(self):
        from resume_analyzer.services.skill_extractor import extract_skills, infer_skills_from_role
        skills = extract_skills("We need a developer experienced in Python, Django, Docker, and PostgreSQL.")
        self.assertIn("Python", skills)
        self.assertIn("Django", skills)
        self.assertIn("Docker", skills)
        self.assertIn("Postgresql", skills)

        role_skills = infer_skills_from_role("Senior Full Stack Engineer")
        self.assertIn("React", role_skills)
        self.assertIn("Python", role_skills)
