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
