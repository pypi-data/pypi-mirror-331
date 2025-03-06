from ..utils.env_initializer import EnvStore


class GenerateLink:
    @staticmethod
    def __get_base_url(courseOfferingId: str) -> str:
        __environment: str = EnvStore().environment.removesuffix("-api")
        __domain: str = EnvStore().domain
        __base_url = (
            f"https://{__environment}{__domain}/learning-center/{courseOfferingId}"
        )
        return __base_url

    @classmethod
    def get_quiz_link(
        cls,
        courseOfferingId: str,
        quizId: str,
    ):
        baseQuizUrl = cls.__get_base_url(courseOfferingId)
        quizUrl = f"/quiz/quiz-learner/quiz-attempt-start/initialize-quiz/{quizId}"
        return baseQuizUrl + quizUrl

    @classmethod
    def get_quiz_report_link(cls, courseOfferingId: str, quizId: str, attemptId: str):
        baseQuizUrl = cls.__get_base_url(courseOfferingId)
        quizReportUrl = f"/quiz/quiz-learner/quiz-report/{attemptId}/{quizId}"
        return baseQuizUrl + quizReportUrl
