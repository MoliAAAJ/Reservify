

def get_overlapping_query(start, end ):
    return [
            # Nueva reserva empieza antes y termina durante una reserva existente
            {
                "start_time": {"$lt": start},
                "end_time": {"$gte": start, "$lte": end}
            },
            # Nueva reserva empieza antes y termina después de una reserva existente
            {
                "start_time": {"$lt": start},
                "end_time": {"$gte": end}
            },
            # Nueva reserva empieza durante una reserva existente y termina durante
            {
                "start_time": {"$gte": start, "$lte": end},
                "end_time": {"$gte": start, "$lte": end}
            },
            # Nueva reserva empieza durante una reserva existente y termina después
            {
                "start_time": {"$gte": start, "$lte": end},
                "end_time": {"$gt": end}
            },
            # Nueva reserva comienza durante una reserva existente
            {
                "start_time": {"$lte": end},
                "end_time": {"$gt": start}
            },
            # Nueva reserva termina durante una reserva existente
            {
                "start_time": {"$lt": end},
                "end_time": {"$gte": start}
            },
            # Nueva reserva completamente contiene una reserva existente
            {
                "start_time": {"$gte": start},
                "end_time": {"$lte": end}
            },
            # Nueva reserva comienza antes de una reserva existente
            {
                "start_time": {"$lt": start},
                "end_time": {"$gte": start}
            },
            # Nueva reserva termina después de una reserva existente
            {
                "start_time": {"$lte": end},
                "end_time": {"$gt": end}
            },
            # Nueva reserva empieza después y termina después
            {
                "start_time": {"$gte": start},
                "end_time": {"$gte": end}
            },
            # Nueva reserva empieza antes de una reserva existente y termina después
            {
                "start_time": {"$lte": start},
                "end_time": {"$gte": end}
            }
            ]