
(define (problem rover-problem)
  (:domain rover-domain)
  (:objects
    rover1 - rover
    localidad1 localidad2 localidad3 localidad4 localidad5 - localidad
    mineral1 mineral2 - mineral
  )
  (:init
    (en rover1 localidad4)  ;; El rover ahora comienza en la localidad 4
    (mineral-en mineral1 localidad1)
    (mineral-en mineral2 localidad2)
    ;; Caminos entre localidades
    (camino localidad3 localidad1)
    (camino localidad1 localidad3)
    (camino localidad3 localidad2)
    (camino localidad2 localidad4)
    (camino localidad3 localidad4)
    (camino localidad4 localidad3)
    (camino localidad4 localidad5)
    (camino localidad5 localidad4)
  )
  
  (:goal
     (and
       (mineral-en mineral1 localidad5)
       (mineral-en mineral2 localidad5)
     )
  )
)