from functools import cache

import couchdb3
from gw_settings_management.setting_management import database_url, database_user, database_password, database_name


class GWDatabaseException(Exception):
    pass



@cache
def get_couchdb(*, override_url=None, override_user=None, override_password=None, override_database_name=None):
    """Get the CouchDB database
    Parameters
    ----------
    override_database_name : str
        Name of the database to use if not the same as defined in the .env"""

    user = database_user()
    password = database_password()
    url = database_url()
    db_name = database_name()

    if override_user is not None:
        user = override_user

    if override_password is not None:
        password = override_password

    if override_url is not None:
        url = override_url


    client = couchdb3.Server(url,
                             user=user,
                             password=password,
                             auth_method='basic')
    all_dbs = client.all_dbs()

    if override_database_name is not None:
        db_name = override_database_name

    if db_name in all_dbs:
        db = client.get(db_name)
    else:
        db = client.create(db_name)

    return db

def get_documents_view(*, override_database_name=None):
    """Get all documents from the CouchDB database
    Parameters
    ----------
    override_database_name : str
        Name of the database to use if not the same as defined in the .env"""
    db = get_couchdb(override_database_name=override_database_name)
    documents = db.all_docs()
    return documents

def get_documents(*, override_database_name=None):
    """Get all Documents from the CouchDB database"""
    db = get_couchdb(override_database_name=override_database_name)
    document_rows = db.all_docs().rows
    documents = [get_document(doc.id) for doc in document_rows]
    return documents


def get_document(doc_id: str, *, create_if_missing=False, override_database_name=None):
    """Retrieve a document from the database.
    Parameters
    ----------
    doc_id : str
        ID of the document to retrieve.
    create_if_missing : bool
        Create an empty document if it does not exist.
    override_database_name : str
        Name of the database to use if not the same as defined in the .env"""
    db = get_couchdb(override_database_name=override_database_name)
    try:
        document = db.get(doc_id)
    except Exception as e:
        document = None
    if document is None:
        if create_if_missing:
            new_doc = {
                "_id": doc_id,
            }
            doc_id, status, rev = db.save(new_doc)
            if not status:
                raise GWDatabaseException(f'Failed to save new document on get {doc_id}')
        else:
            raise GWDatabaseException(f'Document not found ({doc_id})')
        document = db.get(doc_id)
    return document


def post_document(doc_id: str, doc: dict, *, override_database_name=None):
    """Create a new document in the database.
    Parameters
    ----------
    doc_id : str
        ID of the document to create.
    doc : dict
        Document to create.
    override_database_name : str
        Name of the database to use if not the same as defined in the .env
    Raises
    ------
    GWDatabaseException"""
    if "_id" not in doc:
        doc["_id"] = doc_id
    db = get_couchdb(override_database_name=override_database_name)
    if doc["_id"] not in [item.id for item in db.all_docs().rows]:
        doc_id, status, _ = db.create(doc)
        return db.get(doc_id)
    else:
        raise GWDatabaseException(f'Document ({doc_id}) exists - unable to create new document')
    if not status:
        raise GWDatabaseException(f'Failed to create document {doc_id}')


def put_document(doc: dict, *, override_database_name=None):
    """Update a document in the database.
    Parameters
    ----------
    doc : dict
        Document to update.
    override_database_name : str
        Name of the database to use if not the same as defined in the .env
    Raises
    ------
    GWDatabaseException"""
    db = get_couchdb(override_database_name=override_database_name)
    doc_id, status, revision = db.save(doc)
    doc["_rev"] = revision
    if not status:
        raise GWDatabaseException(f'Failed to update document {doc_id}')
    return doc


def delete_document(doc_id: str, *, override_database_name=None):
    """Delete a document from the database.
    Parameters
    ----------
    doc_id : str
        ID of the document to delete.
    override_database_name : str
        Name of the database to use if not the same as defined in the .env
    Raises
    ------
    GWDatabaseException"""
    db = get_couchdb(override_database_name=override_database_name)
    status = db.delete(docid=doc_id, rev=db.rev(doc_id))
    if not status:
        raise GWDatabaseException(f'Failed to delete document {doc_id}')


def find_documents(selector, *, override_database_name=None):
    """
    Find extracts all the documents from the given database what match the criteria in the selector,
    this makes use of bookmarks to repeatedly extract results.
    :param db:
    :param selector:
    :return:
    """
    return_docs = list()
    db = get_couchdb(override_database_name=override_database_name)
    if "selector" in selector:
        selector_dict = selector["selector"]
    elif "fields" not in selector:
        selector_dict = selector
    else:
        selector_dict = {}
    if "fields" in selector:
        fields = selector["fields"]
    else:
        fields = None
    result = db.find(selector=selector_dict, fields=fields)
    while len(result['docs']) > 0:
        bookmark = result['bookmark']
        return_docs.extend(result['docs'])
        result = db.find(selector, bookmark=bookmark)
    return return_docs

