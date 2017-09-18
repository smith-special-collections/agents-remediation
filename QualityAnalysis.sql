/* First, create database called 'agents'
Then, load agents_inmagic.sql
Load a local copy of the ArchivesSpace database as schema 'aspace'

This script will check to make sure that everything in inMagic with contact information is matched to something in ArchivesSpace 

It is asking for ArchivesSpace objects with an inMagic-people authority ID that does NOT have contact information.

If the update was done correctly, this should yield zero records.alter

It may be desirable to update the where statement to check for other kinds of matches*/

SELECT 
    b.id,
    b.agentid,
    b.authority_id,
    inmagic.lastname,
    inmagic.firstname,
    inmagic.classyear,
    inmagic.organization,
    inmagic.address1,
    inmagic.address2,
    inmagic.address3,
    inmagic.city,
    inmagic.state,
    inmagic.zip,
    inmagic.email,
    inmagic.phonehome,
    inmagic.phonework,
    inmagic.cell
FROM
    agents.inmagic AS inmagic
        JOIN
    (SELECT 
        ap.id,
            CONCAT('/agents/people/', ap.id) AS agentid,
            np.id as nameid,
            SUBSTRING_INDEX(nai.authority_id, '_', - 1) AS authority_id,
            np.primary_name,
            np.rest_of_name,
            d.begin,
            d.end,
            d.expression,
            ac.name,
            ac.address_1,
            ac.address_2,
            ac.address_3,
            ac.city,
            ac.region,
            ac.country,
            ac.post_code,
            ac.email,
            t.number,
            ev.value
    FROM
        aspace.agent_person ap
    LEFT JOIN aspace.name_person np ON np.agent_person_id = ap.id
    LEFT JOIN aspace.agent_contact ac ON ap.id = ac.agent_person_id
    LEFT JOIN aspace.enumeration_value ev ON ev.id = np.source_id
    LEFT JOIN aspace.name_authority_id nai ON np.id = nai.name_person_id
    LEFT JOIN aspace.telephone t ON t.agent_contact_id = ac.id
    LEFT JOIN aspace.date d ON d.agent_person_id = ap.id
    WHERE
        ev.value NOT LIKE '%faculty%'
            AND ev.value NOT LIKE '%alum%'
            AND authority_id IS NOT NULL UNION ALL SELECT 
        ace.id,
            CONCAT('/agents/corporate_entities/', ace.id) AS agentid,
            nce.id as nameid,
            SUBSTRING_INDEX(SUBSTRING_INDEX(nai.authority_id, 'source_', 2), 'source_', - 1) AS authority_id,
            nce.primary_name,
            NULL,
            d.begin,
            d.end,
            d.expression,
            ac.name,
            ac.address_1,
            ac.address_2,
            ac.address_3,
            ac.city,
            ac.region,
            ac.country,
            ac.post_code,
            ac.email,
            t.number,
            ev.value
    FROM
        aspace.agent_corporate_entity ace
    LEFT JOIN aspace.name_corporate_entity nce ON nce.agent_corporate_entity_id = ace.id
    LEFT JOIN aspace.agent_contact ac ON ace.id = ac.agent_corporate_entity_id
    LEFT JOIN aspace.enumeration_value ev ON ev.id = nce.source_id
    LEFT JOIN aspace.name_authority_id nai ON nce.id = nai.name_corporate_entity_id
    LEFT JOIN aspace.telephone t ON t.agent_contact_id = ac.id
    LEFT JOIN aspace.date d ON d.agent_corporate_entity_id = ace.id
    WHERE
        ev.value NOT LIKE '%faculty%'
            AND ev.value NOT LIKE '%alum%'
            AND authority_id IS NOT NULL) AS b ON b.authority_id = inmagic.inMagic
WHERE
    (b.city IS NULL AND b.email IS NULL
        AND b.number IS NULL)
LIMIT 10000; 