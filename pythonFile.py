import psycopg2

from flask import Flask, render_template, request

app = Flask(__name__)

def getConn():
    #function to retrieve the password, construct
    #the connection string, make a connection and return it.
    passFile = open("passw.txt", "r")
    passw = passFile.read();
    passFile.close()
    connStr = "host='cmpstudb-01.cmp.uea.ac.uk' port = '5432'\
               dbname= 'rdu17ezu' user='rdu17ezu' password = " + passw
    conn=psycopg2.connect(connStr)          
    return  conn
	
#homepage
@app.route('/')
def home():
    return render_template('hpage.html')

@app.route('/addCustomer', methods=['POST'])
def addCustomer():
    # Creates new customer record given CustomerID, name and email
    try:
        conn=None
        customerID = request.form['customerID']
        name = request.form['name']
        email= request.form['email']     

        conn=getConn()      
        cur = conn.cursor()       
        cur.execute('SET search_path to tickets')
        
        cur.execute('INSERT INTO customer \
                    VALUES (%s, %s, %s)', \
                   [customerID,name,email])
        conn.commit()
        return render_template('hpage.html', msg = 'Record Added')       
    except Exception as e:
        return render_template('hpage.html', msg = 'Record NOT Added ', error=e)
    finally:
        if conn:
            conn.close()
			
@app.route('/addTicket', methods=['POST'])
def addTicket():
    #Create a new support ticket for a customer with respect to given product
    try:
        conn=None
        ticketID = request.form['ticketID']
        problem = request.form['problem']
        status = 'open'
        priority = request.form['priority']
        customerID = request.form['customerID']
        productID = request.form['productID']		

        conn=getConn()      
        cur = conn.cursor()       
        cur.execute('SET search_path to tickets')
        
        cur.execute('INSERT INTO ticket \
                    VALUES (%s, %s, %s, %s,CURRENT_TIMESTAMP, %s, %s)', \
                   [ticketID,problem,status,priority,customerID,productID])
        conn.commit()

        cur.execute('SELECT * FROM ticket WHERE ticketID=%s',[ticketID])
        colNames = [desc[0] for desc in cur.description]
        rows=cur.fetchall()

        return render_template('ticket.html',msg = 'Record Added', \
                                rows=rows, colNames=colNames)
    except Exception as e:
        return render_template('hpage.html', msg1 = 'Record NOT Added ', error1=e)
    finally:
        if conn:
            conn.close()

@app.route('/updateTicket', methods=['POST'])
def updateTicket():
    #Update existing ticket
    try:
        conn=None
        ticketUpdateID = request.form['ticketUpdateID']
        message = request.form['message']
        ticketID = request.form['ticketID']
        staffID = request.form['staffID']		

        conn=getConn()      
        cur = conn.cursor()       
        cur.execute('SET search_path to tickets')
        
        cur.execute('INSERT INTO ticketUpdate \
                    VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s)', \
                   [ticketUpdateID,message,ticketID,staffID])
        conn.commit()

        cur.execute('SELECT * FROM ticketUpdate WHERE ticketUpdateID=%s',\
                    [ticketUpdateID])
        colNames = [desc[0] for desc in cur.description]
        rows=cur.fetchall()

        return render_template('ticketupdate.html', msg = 'Record Added',\
                                rows=rows, colNames=colNames)
       
    except Exception as e:
        return render_template('hpage.html', msg2 = 'Record NOT Added ', error2=e)
    finally:
        if conn:
            conn.close()			
	
@app.route('/closeTicket', methods=['POST'])
def closeTicket():
    #Close properly answered ticket
    try:
        conn=None
        ticketID = request.form['ticketID']

        conn=getConn()      
        cur = conn.cursor()
        cur.execute('SET search_path to tickets')
        cur.execute('SELECT * FROM ticket \
                    WHERE ticket.ticketID=%s \
                    AND EXISTS(SELECT * FROM ticketUpdate \
                    WHERE ticketupdate.ticketID=%s)',[ticketID,ticketID])
        r=cur.fetchall()
        if r:
            cur.execute('SELECT close_ticket(%s)', \
                   [ticketID])			   
            conn.commit()
            return render_template('hpage.html', msg3 = 'Ticket Closed')
        else:
            return render_template('hpage.html', \
                msg3='Ticket cannot be closed or Ticket ID does not exist')
		
    except Exception as e:
        return render_template('hpage.html', msg3 = 'Ticket FAILED to close', error3=e)
    finally:
        if conn:
            conn.close()	
			
@app.route('/showTickets', methods=['GET'])
def showTickets():
    #List all outstanding support tickets along with the time of the last update
    try:
        conn=None
        conn=getConn()  
        cur = conn.cursor()         
        cur.execute('SET search_path to tickets')

        cur.execute('SELECT * FROM o_tickets')        
        colNames = [desc[0] for desc in cur.description]
        rows=cur.fetchall()
        return render_template('openTickets.html', rows=rows, colNames=colNames) 		
    except Exception as e:
        return render_template('hpage.html', msg4 = 'Problem ', error4=e)
    finally:
        if conn:
            conn.close()   
    return render_template('hpage.html')
	
@app.route('/ticketMsg', methods=['POST'])
def ticketMsg():
    #Shows original ticket problem along with all updates in chronological order
    try:
        conn=None
        ticketID = request.form['ticketID']

        conn=getConn()      
        cur = conn.cursor()       
        cur.execute('SET search_path to tickets')
        
        cur.execute('SELECT * FROM customer_ticket WHERE ticketID=%s', \
                   [ticketID])
        colNames = [desc[0] for desc in cur.description]
        rows=cur.fetchall()
        for row in rows:
            problem = row[1]
            status = row[2]
            priority = row[3]
            loggedTime = row[4]
            customerID= row[5]
            productID= row[6]
            name=row[7]
            product=row[8]

        cur.execute('SELECT * FROM answers WHERE ticketID=%s',\
		            [ticketID])
        colN = [desc[0] for desc in cur.description]
        rows2=cur.fetchall()

        if rows:
            return render_template('ticketMsg.html', rows=rows, \
            colNames=colNames,ticketID=ticketID, status= status, \
            problem=problem, priority = priority, loggedTime = loggedTime, \
            name=name, product=product, rows2=rows2, colN=colN)
        else:
            return render_template('hpage.html', msg5 = 'Ticket ID not found')
	
    except Exception as e:
        return render_template('hpage.html', msg5 = 'Problem', error5=e)
    finally:
        if conn:
            conn.close()   
    return render_template('hpage.html')

@app.route('/report', methods=['GET'])
def report():
    #Closed tickets status reports
    try:
        conn=None
        conn=getConn()      
        cur = conn.cursor()
        cur.execute('SET search_path to tickets')
        cur.execute('SELECT * FROM report')
        colNames = [desc[0] for desc in cur.description]
        rows=cur.fetchall()
        if rows:
            return render_template('reports.html', rows=rows, colNames=colNames)
        else:
            return render_template('hpage.html', msg6 = 'There are no closed tickets')
		
    except Exception as e:
        return render_template('hpage.html', msg6 = 'Problem', error6 = e)
    finally:
        if conn:
            conn.close()	
 			
@app.route('/deleteCustomer', methods=['POST'])
def deleteCustomer():
    #Given Customer ID, permanantly remove the customer's details
    try:
        conn=None
        customerID = request.form['customerID']

        conn=getConn()      
        cur = conn.cursor()
        cur.execute('SET search_path TO tickets')
        cur.execute('SELECT * FROM customer\
                    WHERE customerID=%s \
                    AND NOT EXISTS(SELECT * FROM o_tickets \
                    WHERE o_tickets.customerID=%s)',\
                    [customerID,customerID])
        r=cur.fetchall()
        if r:
            cur.execute('SELECT delete_cust(%s)', \
                   [customerID])			   
            conn.commit()
            return render_template('hpage.html', msg7 = 'Customer deleted')
        else:
            return render_template('hpage.html',\
                msg7 = 'Customer still has an open ticket or Customer ID does not exist')

    except Exception as e:
        return render_template('hpage.html', msg7 = 'Ticket FAILED to close',\
                                error7 = e)
    finally:
        if conn:
            conn.close()
 
if __name__ == "__main__":
    app.run(debug = True)