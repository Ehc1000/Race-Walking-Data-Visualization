SELECT Infraction,
       max(case When Infraction = '<' AND CameraPosition = 'Panned' THEN NbrInfractions Else 0 END) NbrPannedBent,
       max(case When Infraction = '<' AND CameraPosition = 'Static' THEN NbrInfractions Else 0 END) NbrStaticBent,
       max(case When Infraction = '~' AND CameraPosition = 'Panned' THEN NbrInfractions Else 0 END) NbrPannedLOC,
       max(case When Infraction = '~' AND CameraPosition = 'Static' THEN NbrInfractions Else 0 END) NbrStaticLOC
FROM (SELECT COUNT(BibNumber) AS NbrInfractions, "<" AS Infraction, "Static" AS CameraPosition
      FROM (SELECT BibNumber
            FROM VideoObservation
            WHERE IDRace = :race_id
              AND KneeAngle > 0
              AND KneeAngle <= 175
            GROUP BY BibNumber
            HAVING COUNT(BibNumber) > 1)
      UNION
      SELECT COUNT(BibNumber) AS NbrInfractions, "~" AS Infraction, "Static" AS CameraPosition
      FROM (SELECT BibNumber, ROUND(AVG(LOCAverage), 1) AS LOCAverage
            FROM VideoObservation
            WHERE IDRace = :race_id
              AND LOCAverage >= 60
            GROUP BY BibNumber
            HAVING COUNT(BibNumber) >= 2)
      UNION
      SELECT COUNT(BibNumber) AS NbrInfractions, "<" AS Infraction, "Panned" AS CameraPosition
      FROM (SELECT BibNumber
            FROM VideoObservationPanned
            WHERE IDRace = :race_id
              AND KneeAngle > 0
              AND KneeAngle <= 175
            GROUP BY BibNumber
            HAVING COUNT(BibNumber) > 1)
      UNION
      SELECT COUNT(BibNumber) AS NbrInfractions, "~" AS Infraction, "Panned" AS CameraPosition
      FROM (SELECT BibNumber, ROUND(AVG(LOCAverage), 1) AS LOCAverage
            FROM VideoObservationPanned
            WHERE IDRace = :race_id
              AND LOCAverage >= 60
            GROUP BY BibNumber
            HAVING COUNT(BibNumber) >= 2)
      ORDER BY Infraction, CameraPosition)


