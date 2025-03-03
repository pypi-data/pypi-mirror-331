import argparse
import sys
import polars as pl
from io import BytesIO, StringIO
from typing import IO
from pathlib import Path


def main() -> None:
    """
    Command line interface for MonarchToMintToReport utility
    """
    kwargs = {
        'description': 'Convert a Monarch transaction export CSV file to a Mint transaction log to open in MintToReport',
        'formatter_class': argparse.RawDescriptionHelpFormatter
    }
    parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument('-i', '--input', type=str, required=True,
                        help='Path to a Monarch export transaction CSV file to read.')

    parser.add_argument('-o', '--output', type=str, required=False, default='monarchtomint-output.csv',
                        help='Path to write out the converted Mint-formatted transaction CSV file.')

    args = parser.parse_args()

    df = _read_csv(args.input, dump = True)
    df = _convert(df, dump = True)
    result = write_mint_csv(df, args.output)
    
    return result


def _read_csv(source: str | Path | IO[str] | IO[bytes] | bytes, dump: False) -> pl.DataFrame:
    """Read a Monarch CSV transaction file, return as a pl.DataFrame

    Parameters
    ----------
    :param source: a compatible type (str, Path, IO[str], IO[bytes], bytes) that points to a Monarch CSV transaction file
    :type source: str, Path, IO[str], IO[bytes], bytes
    :param dump: print the head of the resulting DataFrame (default: False)
    :type dump: bool
    
    Returns
    -----------
    :return: A Polars DataFrame
    :rtype: pl.DataFrame
    """
    try:
        df = pl.read_csv(source, try_parse_dates=True)
    except:
        print("Source CSV file was not able to be parsed properly.  Check that the file exists and is a valid CSV format.")
        sys.exit()
    if dump == True: print(df.head)
    
    return df


def _convert(df: pl.DataFrame, dump: False) -> pl.DataFrame:
    """Read a Monarch CSV transaction file and convert to Mint, return as a pl.DataFrame
    
    Parameters
    ----------
    :param df: DataFrame containing a Monarch-formatted CSV transaction file
    :type input: pl.DataFrame
    :param dump: print the head of the converted DataFrame (default: False)
    :type dump: bool
    
    Returns
    -----------
    :return: A Polars DataFrame converted to Mint format
    :rtype: pl.DataFrame
    """
    
    df = df.with_columns(
        pl.col("Original Statement").alias("Original Description"),
        pl.col("Tags").str.replace(","," ").alias("Labels"),
        pl.col("Account").alias("Account Name"),
        pl.when(pl.col("Amount") > 0)
            .then(pl.lit("credit"))
            .otherwise(pl.lit("debit"))
            .alias("Transaction Type"),
        Description=pl.col("Merchant"),
        Amount=abs(pl.col("Amount"))
        
    ) 
    
    df = df.drop("Original Statement").drop("Merchant")
    
    
    if dump == True: print(df.head)
    
    # export the DataFrame in the expected Mint CSV column order
    df_export=df.select([
        pl.col("Date"),
        pl.col("Description"),
        pl.col("Original Description"), 
        pl.col("Amount"), 
        pl.col("Transaction Type"),
        pl.col("Category"),
        pl.col("Account Name"), 
        pl.col("Labels"), 
        pl.col("Notes")  
    ])    
    
    return df_export


def write_mint_csv(df: pl.DataFrame, file: str | Path | IO[str] | IO[bytes] | bytes) -> bool:
    """Write out the dataframe in CSV format to destination specified via 'file'

    Parameters
    ----------
    :param df: The DataFrame to write
    :type df: pl.DataFrame 
    :param file: The output destination for the CSV file representing Mint-formatted transaction file
    :type output: str, Path, IO[str], IO[bytes], bytes
    
    Returns
    -----------
    :return: If the CSV file was written successfully or not
    :rtype: bool
    """
    
    try:
        df.write_csv(file, date_format=("%m/%d/%Y"))
    except:
        print("Destination for CSV output file was not able to be written to.  Please check that proper parameters were provided.")
        return False
    return True


def convert_csv(source: str | Path | IO[str] | IO[bytes] | bytes, dump: False) -> pl.DataFrame:
    """Public function wrapper: read a Monarch CSV transaction file, return as a pl.DataFrame

    Parameters
    ----------
    :param source: a compatible type (str, Path, IO[str], IO[bytes], bytes) that points to a Monarch CSV transaction file
    :type source: str, Path, IO[str], IO[bytes], bytes
    :param dump: print the head of the resulting DataFrame (default: False)
    :type dump: bool
    
    Returns
    -----------
    :return: A Polars DataFrame
    :rtype: pl.DataFrame
    """
    
    df = _read_csv(source, dump)
    df = _convert(df)
    return df


if __name__ == '__main__':
    main()    