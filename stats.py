#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql


def nowords(sourcelang="lv"):

    if sourcelang == "lv":
        targetlang = "et"
    else:
        targetlang = "lv"

    filenamestem = "ilmasisseminevata"
    filetitle = sourcelang + "-" + filenamestem
    fileheading = "Puhastatud mõisted, kus esimene <i>" + sourcelang + "</i> termin pole märgitud sisseminevaks"
    fileheader = """<html>
                    <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
                    <title>""" + filetitle + """</title>
                    </head>
                    <body>
                    <h3>""" + fileheading + """</h3><p><p>"""
    filefooter = """</body>
                    </html>"""

    cnx = pymysql.connect(host='termbases.eu', user='arvi', passwd='v2MBxSa73NNsTaHX', db='tb_live')

    cursor = cnx.cursor()


    comparequery = ("""SELECT COUNT(t.term), COUNT(DISTINCT(t.term)), COUNT(DISTINCT(t.concept_id), t.lang)
                    FROM termeki_concepts c
                    LEFT JOIN termeki_terms t ON t.concept_id = c.concept_id
                    LEFT JOIN termeki_concept_attributes_boolean cab ON (c.concept_id=cab.concept_id AND cab.attribute_id=36778)
                    WHERE t.termbase_id=4355781
                    AND cab.attribute_value = 1
                    AND t.in_dictionary = 1
                    AND t.term REGEXP '.*'
                    AND t.is_deleted = 0
                    GROUP BY t.lang""")

    cursor.execute(comparequery) #, (sourcelang, ))
    result = cursor.fetchall()

    tk = 3610

    moisteid = result[0][2] + tk
    eestiterm = result[0][0] + tk
    eestitermdistinct = result[0][1] + tk
    eestitahendustearv = round(eestiterm/eestitermdistinct, 2)
    eestisonupermoiste = round(eestiterm/moisteid, 2)

    nowstring =  "<p>Puhastatud on " + str(moisteid) + " mõistet.</p>"
    nowstring += "<p>Neis on " + str(eestiterm) + " eesti märksõna, millest " + str(eestitermdistinct) + " erikujulist.<br> "
    nowstring += "Ühel eesti märksõnal on seega keskmiselt " + str(eestitahendustearv) + " tähendust.<br> "
    nowstring += "Ühel mõistel on keskmiselt " + str(eestisonupermoiste) + " eesti sõna.</p>"

    latiterm = result[1][0] + tk
    latitermdistinct = result[1][1] + tk
    latitahendustearv = round(latiterm/latitermdistinct, 2)
    latisonupermoiste = round(latiterm/moisteid, 2)

    nowstring += "<p>Neis on " + str(latiterm) + " läti märksõna, millest " + str(latitermdistinct) + " erikujulist.<br> "
    nowstring += "Ühel läti märksõnal on seega keskmiselt " + str(latitahendustearv) + " tähendust.<br> "
    nowstring += "Ühel mõistel on keskmiselt " + str(latisonupermoiste) + " läti sõna.</p>"


    return nowstring



















    comparewordlist = list()
    for headword in headwordlist:
        comparewordlist.append(headword[0])


    mainquery = ("""SELECT t.term, t.concept_id
                    FROM termeki_concepts c
                    LEFT JOIN termeki_terms t ON t.concept_id = c.concept_id
                    LEFT JOIN termeki_concept_attributes_boolean cab ON (c.concept_id=cab.concept_id AND cab.attribute_id=36778)
                    WHERE t.termbase_id=4355781
                    AND cab.attribute_value = 1
                    AND (t.in_dictionary = 0)
                    AND t.in_dictionary = 0 AND t.line = (
                      SELECT min(tt.line)
                      FROM termeki_terms tt
                      WHERE tt.termbase_id=4355781
                      AND tt.is_deleted = 0
                      AND tt.concept_id = t.concept_id
                      AND tt.lang = t.lang
                    )
                    AND t.lang = %s
                    AND t.is_deleted = 0
                    AND t.term REGEXP '.*'
                    AND t.term IN """+ str(tuple(comparewordlist)) + """
                    ORDER BY t.term, t.homonym_line""")



# getting filtered
    cursor.execute(mainquery, (sourcelang, ))
    headwordlist = cursor.fetchall()
#    print(len(headwordlist), "filtered headwords in", sourcelang)

#    print(headwordlist)

    articlelist = dict()
    commalist = dict()

    headwordnumber = 0

    homono = 1
    prevterm = ""
    prevarticle = ""
    prevsortterm = ""

    for headword in headwordlist:
        concept = headword[1]
        term = headword[0]

        if term == prevterm:
            homono += 1
        else:
            homono = 1

        equivsquery = ("""SELECT term, in_dictionary, line, is_preferred FROM termeki_terms t
                WHERE t.termbase_id=4355781
                AND t.concept_id = %s
                AND t.lang = %s
                AND t.in_dictionary = 1
                AND t.is_deleted = 0
                ORDER BY t.is_preferred DESC, t.line""")

        subjectquery = ("""SELECT subject_name FROM termeki_concept_subjects cs
                LEFT JOIN termeki_termbase_subject_translations st ON cs.subject_id = st.subject_id
                WHERE cs.concept_id = %s""")


        cursor.execute(equivsquery, (str(concept), targetlang))

        equivslist = cursor.fetchall()

        equivsline = ""
        for equiv in equivslist:
            if equivsline == "":
                equivsline = equiv[0]
            else:
                equivsline += ", " + equiv[0]

        cursor.execute(equivsquery, (str(concept), sourcelang))

        synoslist = cursor.fetchall()

        synosline = ""
        for syno in synoslist:
            if syno[0] != term:
                if synosline == "":
                    synosline = syno[0]
                else:
                    synosline += ", " + syno[0]

        if synosline != "":
            synosline = " (" + synosline + ")"


        cursor.execute(subjectquery, (str(concept), ))

        subjectslist = cursor.fetchall()

#        print(term, subjectslist)

        subjectsline = ""
        for subj in subjectslist:
            if subjectsline == "":
                subjectsline = subj[0]
            else:
                subjectsline += ", " + subj[0]

        if subjectsline != "":
            subjectsline = " [" + str(subjectsline) + "]"

        sortterm = term + " " + str(homono) + "0\t"

#        if term.startswith("###"):
#            sortterm = term[2:] + "1\t"

        if homono == 1:
            homoline = ""
            article = """<a href="http://term.eki.ee/termbase/view/4355781/#/concept/edit/""" + str(concept) + """/" target="_blank">""" + term + homoline + "</a>" + synosline + subjectsline + " - " + equivsline
            articlelist[sortterm] = article

            prevsortterm = sortterm
            homoline = " 1"
            prevarticle = """<a href="http://term.eki.ee/termbase/view/4355781/#/concept/edit/""" + str(concept) + """/" target="_blank">""" + term + homoline + "</a>" + synosline + subjectsline + " - " + equivsline

        else:
            homoline = " " + str(homono)
            article = """<a href="http://term.eki.ee/termbase/view/4355781/#/concept/edit/""" + str(concept) + """/" target="_blank">""" + term + homoline + "</a>" + synosline + subjectsline + " - " + equivsline
            articlelist[sortterm] = article

            if homono == 2:
                articlelist[prevsortterm] = prevarticle    #overwrite the previous numberless article with a 1-numbered one


        prevterm = term

        commalist[sortterm] = term

        headwordnumber += 1
        if (headwordnumber == 1 or headwordnumber % 100 == 0):
            print(headwordnumber, article)


    articlefilename =  filenamestem + "-" + sourcelang + "-art" + ".txt"
    commafilename =  filenamestem + "-" + sourcelang + "-com" + ".txt"
    htmlfilename = filenamestem + "-" + sourcelang + ".html"

#    write_dict(articlelist, articlefilename)
#    write_dict(articlelist, htmlfilename, header=fileheader, footer=filefooter, style="html")
#    write_dict(commalist, commafilename, style="comma")


    cursor.close()
    cnx.close()
