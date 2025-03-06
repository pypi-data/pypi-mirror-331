import mlflow
import service.aop
class CalculatorService:
    @staticmethod
    @service.aop.func_aspect
    def add(num1, num2):
        num1 = CalculatorService.subtract(num1, num2)
        return num1 + num2

    @staticmethod
    @mlflow.trace
    def subtract(num1, num2):
        return num1 - num2

    @staticmethod
    @mlflow.trace
    def multiply(num1, num2):
        return num1 * num2

    @staticmethod
    @service.aop.func_aspect
    def divide(num1, num2):
        return num1 / num2