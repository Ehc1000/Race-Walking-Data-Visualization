UPDATE AthleteStaging
SET IDAthlete =
        (SELECT IDAthlete
         FROM Athlete
         WHERE Athlete.FirstName = AthleteStaging.FirstName
           AND Athlete.LastName = AthleteStaging.LastName
           AND Athlete.CountryCode = AthleteStaging.CountryCode)
WHERE EXISTS (SELECT IDAthlete
              FROM Athlete
              WHERE Athlete.FirstName = AthleteStaging.FirstName
                AND Athlete.LastName = AthleteStaging.LastName
                AND Athlete.CountryCode = AthleteStaging.CountryCode)