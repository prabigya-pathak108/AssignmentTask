import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Airport, Airline, Flight
from sqlalchemy.engine import Engine
import io
import pandas as pd
from sqlalchemy.orm import sessionmaker

# Create session
def get_session():
    return SessionLocal()

def insert_airports():
    df = pd.read_csv("../kaggle_dataset/airports.csv")

    session = get_session()
    try:
        for _, row in df.iterrows():
            airport = Airport(
                iata_code=row["IATA_CODE"],
                airport=row["AIRPORT"],
                city=row["CITY"],
                state=row["STATE"],
                country=row["COUNTRY"],
                latitude=row["LATITUDE"],
                longitude=row["LONGITUDE"]
            )
            session.add(airport)
        session.commit()
        print("✅ Airports data inserted successfully!")
    except Exception as e:
        session.rollback()
        print("❌ Error inserting airports:", e)
    finally:
        session.close()

def insert_airlines():
    df = pd.read_csv("../kaggle_dataset/airlines.csv")

    session = get_session()
    try:
        for _, row in df.iterrows():
            airline = Airline(
                iata_code=row["IATA_CODE"],
                airline=row["AIRLINE"]
            )
            session.add(airline)
        session.commit()
        print("✅ Airlines data inserted successfully!")
    except Exception as e:
        session.rollback()
        print("❌ Error inserting airlines:", e)
    finally:
        session.close()
def copy_from_flights(engine: Engine, df: pd.DataFrame, table_name: str = "flights"):
    output = io.StringIO()
    df.to_csv(output, sep='\t', header=False, index=False, na_rep='NULL')  
    output.seek(0)  

    with engine.raw_connection() as conn:
        with conn.cursor() as cursor:
            cursor.copy_from(output, table_name, sep='\t', null='NULL')
        conn.commit()




def insert_flights():
    num_of_errors=1
    try:
        # Read the CSV file
        df = pd.read_csv("../kaggle_dataset/flights_demo.csv")
        df.dropna(subset=['AIRLINE'], inplace=True)  # Drop rows where AIRLINE is NaN

        # Convert columns to numeric, coercing errors to NaN
        for col in df.columns:
            if df[col].dtype != 'object':  # Skip columns that are already numeric
                df[col] = pd.to_numeric(df[col], errors='coerce')

        print(f"DataFrame shape after conversion: {df.shape}")

        # Replace "NaN" string values with actual None (None is the equivalent of SQL NULL)
        df.replace("NaN", None, inplace=True)

        # Handle any NaN values that are not allowed in the database (for numeric columns)
        # You can either drop NaN values or fill them with a default value (e.g., 0)
        df.fillna(0, inplace=True)  # Filling NaN with 0 or use an appropriate fill value

        # Get the database session (assumes a function get_session exists)
        session = get_session()

        print(f"DataFrame shape after cleaning: {df.shape}")

        # Iterate over each row in the DataFrame and insert into the database
        for _, row in df.iterrows():
            try:
                # Create a Flight object for each row in the DataFrame
                flight = Flight(
                    year=row["YEAR"],
                    month=row["MONTH"],
                    day=row["DAY"],
                    day_of_week=row["DAY_OF_WEEK"],
                    airline=row["AIRLINE"],
                    flight_number=row["FLIGHT_NUMBER"],
                    tail_number=row["TAIL_NUMBER"],
                    origin_airport=row["ORIGIN_AIRPORT"],
                    destination_airport=row["DESTINATION_AIRPORT"],
                    scheduled_departure=row["SCHEDULED_DEPARTURE"],
                    departure_time=row["DEPARTURE_TIME"],
                    departure_delay=row["DEPARTURE_DELAY"],
                    taxi_out=row["TAXI_OUT"],
                    wheels_off=row["WHEELS_OFF"],
                    scheduled_time=row["SCHEDULED_TIME"],
                    elapsed_time=row["ELAPSED_TIME"],
                    air_time=row["AIR_TIME"],
                    distance=row["DISTANCE"],
                    wheels_on=row["WHEELS_ON"],
                    taxi_in=row["TAXI_IN"],
                    scheduled_arrival=row["SCHEDULED_ARRIVAL"],
                    arrival_time=row["ARRIVAL_TIME"],
                    arrival_delay=row["ARRIVAL_DELAY"],
                    diverted=row["DIVERTED"],
                    cancelled=row["CANCELLED"],
                    cancellation_reason=row["CANCELLATION_REASON"],
                    air_system_delay=row["AIR_SYSTEM_DELAY"],
                    security_delay=row["SECURITY_DELAY"],
                    airline_delay=row["AIRLINE_DELAY"],
                    late_aircraft_delay=row["LATE_AIRCRAFT_DELAY"],
                    weather_delay=row["WEATHER_DELAY"]
                )
                session.add(flight)
                session.commit()
            except Exception as row_error:
                print("Error Count:",num_of_errors)
                num_of_errors+=1
                session.rollback()
                continue  # Skip this row and continue with the next one
        
        print("✅ Flights data inserted successfully!")

    except Exception as e:
        # If there is an error in the overall insert process, rollback the session
        session.rollback()
        print(f"❌ Error inserting flights: {e}")

    finally:
        # Always close the session after processing
        session.close()



if __name__ == "__main__":
    insert_airports()
    insert_airlines()
    insert_flights()
