import math

def resolver_ecuacion_cuadratica(a, b, c):
    """Resuelve ecuaciones cuadráticas ax^2 + bx + c = 0"""
    discriminante = b**2 - 4*a*c
    if discriminante < 0:
        return "No hay soluciones reales"
    x1 = (-b + math.sqrt(discriminante)) / (2 * a)
    x2 = (-b - math.sqrt(discriminante)) / (2 * a)
    return x1, x2
