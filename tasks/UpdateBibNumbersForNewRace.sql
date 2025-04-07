UPDATE Athlete
SET BibNumber =
        (SELECT BibNumber FROM AthleteStaging WHERE Athlete.IDAthlete = AthleteStaging.IDAthlete)
WHERE EXISTS (SELECT BibNumber FROM AthleteStaging WHERE Athlete.IDAthlete = AthleteStaging.IDAthlete)